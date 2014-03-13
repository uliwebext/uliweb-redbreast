from pyPEG import *
import re
import types

_ = re.compile

class ParserError(Exception):pass

class WorkflowGrammar(dict):
    def __init__(self):
        peg, self.root = self._get_rules()
        self.update(peg)
        
    def _get_rules(self):
        # 0 ?
        # -1 *
        # -2 +
        #basic
        def ws(): return _(r'\s+')
        def space(): return _(r'[ \t]+')
        def eol(): return _(r'\r\n|\r|\n')
        def iden(): return _(r'[a-zA-Z_][a-zA-Z_0-9]*')
        def colon(): return _(r':')
        def blankline(): return 0, space, eol
        def double_tripple(): return 0, ws, _(r'"""(.*?)"""', re.S), blankline
        def single_tripple(): return 0, ws, _(r"'''(.*?)'''", re.S), blankline
        def tripple(): return [single_tripple, double_tripple]
        def comment_line(): return 0, space, _(r'#[^\r\n]*'), eol

        #task
        def task_def_head(): return 0, space, _(r'task'), space, task_def_name, 0, task_def_extend, 0, space, colon, blankline
        def task_def_name(): return iden
        def task_def_parent(): return iden
        def task_def_desc(): return tripple
        def task_def_end(): return 0, space, _(r'end'), blankline
        def task_def_extend(): return 0, space, _(r'\('), 0, space, task_def_parent, 0, space, _(r'\)')
        def task_code_name(): return iden
        def task_code_head(): return 0, space, _(r'code'), 0, space, task_code_name, 0, space, colon, blankline
        def task_code_body(): return _(r'(.*?)end[ \t]*$', re.M|re.S)
        def task_code(): return task_code_head, task_code_body, blankline        
        def kwarg_name(): return iden
        def kwarg_value(): return _(r'[^\r\n]+'), blankline
        def kwarg(): return 0, space, kwarg_name, 0, space, colon, 0, space, kwarg_value
        def task(): return task_def_head, 0, task_def_desc, -1, [kwarg, task_code, blankline, comment_line], task_def_end
    
        #process
        def process_def_head(): return 0, space, _(r'process'), space, process_def_name, 0, space, colon, blankline
        def process_def_name(): return iden
        def process_def_alias_task(): return iden
        def process_def_desc(): return tripple
        def process_task_alias(): return iden, -1, (0, space, _(r','), 0, space, iden), blankline
        def process_task_def(): return 0, space, process_def_alias_task, 0, space, _(r'as'), 0, space, process_task_alias
        def process_tasks_head(): return 0, space, _(r'tasks'), 0, space, colon, blankline
        def process_tasks():
            return process_tasks_head, -1, [process_task_def, blankline, comment_line], 0, space, _(r'end'), blankline
        def process_flows_head(): return 0, space, _(r'flows'), 0, space, colon, blankline
        def process_flows_line(): return -2, (0, space, iden, 0, space, _(r'->')), 0, space, iden, blankline
        def process_flows():
            return process_flows_head, -1, [process_flows_line, blankline, comment_line], 0, space, _(r'end'), blankline
        def process_code_name(): return iden, 0, (_(r'.'), iden)
        def process_code_head(): return 0, space, _(r'code'), 0, space, process_code_name, 0, space, colon, blankline
        def process_code_body(): return _(r'(.*?)end[ \t]*$', re.M|re.S)
        def process_code(): return process_code_head, process_code_body, blankline
        def process(): return process_def_head, 0, process_def_desc, -1, [kwarg, process_tasks, process_flows, process_code, blankline, comment_line], 0, space, _(r'end'), blankline
    
        #workflow
        def workflow(): return 0, ws, -1, [task, process, blankline, comment_line]
    
        peg_rules = {}
        for k, v in ((x, y) for (x, y) in locals().items() if isinstance(y, types.FunctionType)):
            peg_rules[k] = v

        return peg_rules, workflow
    
    def parse(self, text, root=None, skipWS=False, **kwargs):
        if not text:
            text = '\n'
        if text[-1] not in ('\r', '\n'):
            text = text + '\n'
        text = re.sub('\r\n|\r', '\n', text)
        return parseLine(text, root or self.root, skipWS=skipWS, **kwargs)
    
class SimpleVisitor(object):
    def __init__(self, grammar=None):
        self.grammar = grammar

    def visit(self, nodes, root=False):
        buf = []
        if not isinstance(nodes, (list, tuple)):
            nodes = [nodes]
        if root:
            method = getattr(self, '__begin__', None)
            if method:
                buf.append(method())
        for node in nodes:
            if isinstance(node, (str, unicode)):
                buf.append(node)
            else:
                if hasattr(self, 'before_visit'):
                    buf.append(self.before_visit(node))
                method = getattr(self, 'visit_' + node.__name__ + '_begin', None)
                if method:
                    buf.append(method(node))
                method = getattr(self, 'visit_' + node.__name__, None)
                if method:
                    buf.append(method(node))
                else:
                    if isinstance(node.what, (str, unicode)):
                        buf.append(node.what)
                    else:
                        buf.append(self.visit(node.what))
                method = getattr(self, 'visit_' + node.__name__ + '_end', None)
                if method:
                    buf.append(method(node))
                if hasattr(self, 'after_visit'):
                    buf.append(self.after_visit(node))
        
        if root:
            method = getattr(self, '__end__', None)
            if method:
                buf.append(method())
        return ''.join(buf)

class WorkflowVisitor(SimpleVisitor):
    def __init__(self, grammar=None):
        self.grammar = grammar
        self.tasks = {}
        self.processes = {}
        
    def visit_task(self, node):
        t = {'codes':{}}
        name = node.find('task_def_name').text
        parent = node.find('task_def_parent')
        if parent:
            t_parent = self.tasks.get(parent.text)
            if not t_parent:
                raise ParserError("Can't find Task %s definition" % parent.text)
            t.update(t_parent)
        
        desc = node.find('task_def_desc')
        if desc:
            t['desc'] = desc.text.strip()[3:-3].strip()
            
        for k in node.find_all('kwarg'):
            n = k.find('kwarg_name').text.strip()
            v = k.find('kwarg_value').text.strip()
            t[n] = v

        for k in node.find_all('task_code'):
            _n = k.find('task_code_name').text
            code = k.find('task_code_body').text
            fname, funcname = self._format_func_name(name, _n)
            _code = self._format_func_code(funcname, code)
            if _code:
                t['codes'][fname] = _code
             
        t['name'] = name
        self.tasks[name] = t
        return ''
    
    def _format_func_name(self, processname, funcname):
        _name = processname + '_' + funcname.replace('.', '_')
        return _name, 'def ' + _name + '():'
    
    def _format_func_code(self, funcname, code):
        def find_indent(lines):
            for i in range(1, len(lines)):
                line = lines[i]
                _line = line.lstrip()
                if _line.startswith('#'):
                    continue
                else:
                    diff = len(line) - len(_line)
                    if diff == 0:
                        indent = 4
                    else:
                        indent = 4 - diff
                    return indent
                
        s = [funcname]
        s.extend(code.splitlines()[:-1])
        indent = -1
        space = ''
        index = 0
        for i in range(1, len(s)):
            if indent == -1:
                indent = find_indent(s)
                if indent >= 0:
                    space = ' ' * indent
                else:
                    index = -indent
            if indent >= 0:
                s[i] = space + s[i]
            else:
                s[i] = s[i][index:]
        
        if len(s) == 1:
            return ''
        return '\n'.join(s)
    
    def visit_process(self, node):
        p = {'tasks':{}, 'flows':[], 'codes':{}}
        name = node.find('process_def_name').text
        
        desc = node.find('process_def_desc')
        if desc:
            p['desc'] = desc.text.strip()[3:-3].strip()
        
        for k in node.find_all('kwarg'):
            n = k.find('kwarg_name').text.strip()
            v = k.find('kwarg_value').text.strip()
            p[n] = v
        
        for t in node.find_all('process_task_def'):
            _task = t.find('process_def_alias_task').text
            aliases = t.find('process_task_alias')
            for alias in aliases.find_all('iden'):
                _n = alias.text
                p['tasks'][_n] = _task
                
        for t in node.find_all('process_flows_line'):
            flow_begin = None
            for x in t.find_all('iden'):
                _n = x.text
                if not flow_begin:
                    flow_begin = _n
                else:
                    p['flows'].append((flow_begin, _n))
                    flow_begin = _n
                if _n not in p['tasks']:
                    p['tasks'][_n] = _n
                    
        for t in node.find_all('process_code'):
            _n = t.find('process_code_name').text
            code = t.find('process_code_body').text
            fname, funcname = self._format_func_name(name, _n)
            _code = self._format_func_code(funcname, code)
            if _code:
                p['codes'][fname] = _code
        
        p['name'] = name
        self.processes[name] = p
        return ''
    
def parse(text, raise_error=True):
    g = WorkflowGrammar()
    resultSoFar = []
    result, rest = g.parse(text, resultSoFar=resultSoFar, skipWS=False)
    if raise_error and rest:
        raise ParserError("Parse is not finished, the rest is [%s]" % rest)
    v = WorkflowVisitor(g)
    v.visit(result, True)
    return v.tasks, v.processes

def parseFile(filename, raise_error=True):
    with open(filename) as f:
        text = f.read()
        return parse(text, raise_error)