__version__ = "2.3"

### Feedback
# Fehler bitte melden an urs-martin.kuenzi@ffhs.ch

try:
    import pandas as pd
except:
    print("Warning: Panda is not installed")

try:
    from warnings import deprecated
except:
    # Für Python Versionen < 3.13
    import warnings
    from functools import wraps


    def deprecated(warning_text):
        def decorator(cls):
            original_init = cls.__init__

            @wraps(original_init)
            def new_init(self, *args, **kwargs):
                warnings.warn(warning_text, UserWarning)
                original_init(self, *args, **kwargs)

            cls.__init__ = new_init
            return cls

        return decorator


class Registermaschine:
    MAX_STEPS = 5000

    def __init__(self, src, command_classes=None, empty_gen=str):
        """
        Initialisiert und kompiliert Registermaschinenprogramm.
        
        :param src: Quellcode eines Registermaschinenprogramms.
        :param command_classes: Liste mit den Klassen der Befehle für die Registermaschine.
        :param empty_gen: Konstruktor für neues (leeres) Register.
        """
        self.src = src
        self.empty_gen = empty_gen
        self.__parse(command_classes)
        self._last_run = None

    def __parse(self, command_classes):
        """ 
        Parser für ein Registermaschinenprogramm. 
        :param command_types: 
        """
        if command_classes is None:
            command_classes = (POP, PUSH, STOP,
                               IF_EMPTY, IF_EQUAL, SWITCH, GOTO, CALL)
        cmd_classes_dict = {cls.__name__: cls for cls in command_classes}
        self.code = {}
        commands = []
        marks = {}
        self.code[":main:"] = (commands, marks, ())
        lines = self.src.split('\n')
        for line in lines:
            line_s = line.strip()
            if len(line_s) == 0 or line_s[:1] == '#':
                continue
            tokens = line_s.split()
            if ':' == tokens[0][-1]:
                mark = tokens[0][:-1]
                if len(mark) == 0:
                    raise ValueError(f"Leere Sprungadressen sind nicht erlaubt in in\n{line}.")
                if mark in marks:
                    raise ValueError(f"Sprungaddresse '{mark}' in\n{line}\n wurde schon verwendet.")

                marks[mark] = len(commands)
                tokens = tokens[1:]
            if len(tokens) == 0 or tokens[0][:1] == "#":
                commands.append(NOP())
            elif tokens[0] == "SUB":
                # TODO validiere vorangehendes Subprogramm.
                if len(tokens) < 2:
                    raise ValueError(f"SUB sollte das aufzufufende Subprogramm angeben")
                commands = []
                marks = {}
                self.code[tokens[1]] = (commands, marks, tokens[2:])
            else:
                cls = cmd_classes_dict[tokens[0]]
                cmd = cls(line, *tokens[1:])
                commands.append(cmd)

    def __call__(self, *args):
        """
        Führt ein Registerprogramm aus.
        :param args: Die Registerinhalte für den Start der Registermaschine.
        :return: Der Registerinhalt der Maschine nach einem Run.
        """
        self._last_run = []
        registers = Registers(self.empty_gen)
        for i in range(len(args)):
            registers[i] = args[i]
        context = Context()
        callstack = []
        actual = ":main:"
        commands, marks, params = self.code[actual]
        command_nr = 0
        for _ in range(Registermaschine.MAX_STEPS):
            if command_nr < 0:
                if len(callstack) == 0:
                    break
                else:
                    actual, command_nr = callstack.pop()
                    commands, marks, params = self.code[actual]
                    context = context.outer
            else:
                if command_nr >= len(commands):
                    cmd = STOP("")
                else:
                    cmd = commands[command_nr]
                self._last_run.append(
                    [len(callstack) * '_ ' + actual, 1 + command_nr, cmd] + registers.content())
                ret = cmd.evaluate(registers, context)
                if ret is None:
                    command_nr += 1
                elif isinstance(ret, str):
                    command_nr = marks[ret]
                elif ret == ():
                    command_nr = -1
                elif isinstance(ret, tuple):
                    callstack.append((actual, command_nr + 1))
                    actual = ret[0]
                    commands, marks, params = self.code[actual]
                    command_nr = 0
                    if len(ret) != len(params) + 1:
                        raise TypeError(
                            f"Subprogramm {actual} benötigt {len(params)} Parameter, aber es sind {len(ret) - 1} angegeben.")
                    context = Context(context)
                    for key, val in zip(params, ret[1:]):
                        context[key] = val
                else:
                    assert False, f"Wrong return type of instruction evaluation: {type(ret)} is not supported."
        else:
            raise RuntimeError(f"""Maximale Anzahl von Schritten ({Registermaschine.MAX_STEPS}) überschritten.
Passe allenfalls Registermaschine.MAX_STEPS an.""")
        return registers.content()

    """
    Liefert den Verlauf des letzten Durchlaufes der Registermaschine als DataFrame.
    :param align_left: Parameter gibt an, ob innerhalb einer Zelle linksbündig ausgerichtete werden sollte.
             Default ist True;  
             Wenn ausgerichtet wird, dann wird ein Styler-Objekt zurückgegeben, sonst eine DataFrame. 
    """

    def last_run(self, align_left=True):
        last_run = self._last_run
        try:
            df = pd.DataFrame(last_run)
            df.fillna(self.empty_gen(), inplace=True)
            df.columns = ['Sub', 'Nr', "Cmd"] + ['R' + str(i) for i in range(df.shape[1] - 3)]
            cmds = df[["Cmd"]]
            df = df.drop("Cmd", axis=1)
            df = pd.concat((df, cmds), axis=1)
            if not align_left:
                return df
            df.style.set_properties(subset=["Cmd"], **{'text-align': 'left'})
            dfStyler = df.style.set_properties(**{'text-align': 'left'})
            dfStyler.set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'left')]},
                {'selector': 'td', 'props': [('text-align', 'left')]},
            ])
            return dfStyler
        except Exception as err:
            print(err)
            return last_run


class _MyDict(dict):
    def __init__(self, *args, **nargs):
        super().__init__(*args, **nargs)

    def __str__(self):
        def item_to_str(item):
            key, val = item
            return val if key is None else key + ':' + val

        return '  '.join([item_to_str(item) for item in self.items()])


class Registers:
    """
    Ein System von Registern für eine Registermaschine.
    Die Anzahl Register wird nicht festgelegt, 
    die einzelnen Register werden als leere Register
    bei Bedarf erstellt.
    """

    def __init__(self, empty_gen=str):
        self.empty_gen = empty_gen
        self.registers = [self.empty_gen()]

    def __getitem__(self, n):
        self.__provide_registers(n)
        return self.registers[n]

    def __setitem__(self, n, val):
        self.__provide_registers(n)
        self.registers[n] = val

    def __provide_registers(self, n):
        while n >= len(self.registers):
            self.registers.append(self.empty_gen())

    def content(self):
        """
        Liefert die Registerinhalte als Liste
        """
        return self.registers[:]


class Context:
    def __init__(self, outer=None):
        self.outer = outer
        self.mappings = {}

    def __getitem__(self, key):
        if key in self.mappings:
            key = self.mappings[key]
        if not key.startswith('$'):
            try:
                return int(key)
            except:
                raise ValueError(
                    "Eine Registerbezeichnung muss eine Ganzzahl oder ein Parameter der Form '$...' sein, ist aber {key}")
        elif self.outer == None:
            raise KeyError(f"Parameter {key} ist nicht definiert")
        else:
            return self.outer[key]

    def __setitem__(self, key, value):
        if not key.startswith('$') or len(key) < 2:
            raise ValueError(
                f"Illegaler Parametername '{key}'; Parameternamen beginnen mit einem '$' end besitzen Länge >= 2")
        self.mappings[key] = value

    def __repr__(self):
        res = "Contex(" + str(self.mappings)
        if self.outer:
            res += ",\nouter=" + repr(self.outer)
        res += ')'
        return res


class Instruction:
    """
    Basisklasse für Befehle der Registermaschine.
    """

    def __init__(self, src):
        self.src = src

    def __str__(self):
        return f"{type(self).__name__}  {'  '.join((str(arg) for (key, arg) in self.__dict__.items() if key != 'src'))}"

    def __repr__(self):
        return f"{type(self).__name__}({', '.join((repr(arg) for (key, arg) in self.__dict__.items() if key != 'src'))})"

    # TODO erweitern und einbetten!
    @classmethod
    def __check_arguments(cls, code, args):
        cmd = cls.__name__
        if len(code) != len(args):
            raise TypeError(f"Der Befehl {cmd} benötigt {len(code)} Argumente, gegeben wurden {len(args)}")
        for i in range(len(args)):
            if code[i] == 'r':
                if not args[i].isnumeric():
                    raise ValueError(f"Das {i + 1}. Argument von {cmd} sollte eine Zahl sein, ist aber {args[i]}")
            elif code[i] == 'c':
                if len(args[i]) != 1:
                    raise ValueError(
                        f"Das {i + 1}. Argument von {cmd} sollte ein einzelnes Symbol sein, ist aber {args[i]}")


class POP(Instruction):
    """
    POP Befehl: Entfernt oberstes Zeichen vom angegebenen Register und 
    springt je nach Wert dieses Zeichens zu einer angegebenen Marke oder zur nächsten Anweisung.
    Syntax: POP reg_nr [:empty_mark] {char:mark} [else_mark] 
    """

    def __init__(self, src, reg_nr, *args):
        super().__init__(src)
        self.reg_nr = reg_nr
        args = [[':', arg[2:]] if arg.startswith("::") else arg.split(':', maxsplit=1) for arg in args]
        args = [[None, arg[0]] if len(arg) == 1 else arg for arg in args]
        arg_keys = set((arg[0] for arg in args))
        if len(arg_keys) < len(args):
            raise ValueError(f"Mehrdeutige Sprunganweisung in\n{self.src}")
        self.marks = _MyDict(dict(args))

    def evaluate(self, registers, context):
        reg = registers[context[self.reg_nr]]
        top = reg[-1:]
        if len(reg) > 0:
            registers[context[self.reg_nr]] = reg[:-1]

        if top in self.marks.keys():
            return self.marks[top]
        elif None in self.marks.keys():
            return self.marks[None]
        else:
            return None


class SWITCH(Instruction):
    """
    SWITCH Befehl
    Syntax: SWITCH reg_nr [:empty_mark] {char:mark} [else_mark] 
    """

    def __init__(self, src, reg_nr, *args):
        super().__init__(src)
        self.reg_nr = reg_nr
        args = [[':', arg[2:]] if arg.startswith("::") else arg.split(':', maxsplit=1) for arg in args]
        args = [[None, arg[0]] if len(arg) == 1 else arg for arg in args]
        arg_keys = set((arg[0] for arg in args))
        if len(arg_keys) < len(args):
            raise ValueError(f"Mehrdeutige Sprunganweisungen in\n{self.src}.\n")
        self.marks = _MyDict(dict(args))

    def evaluate(self, registers, context):
        top = registers[context[self.reg_nr]][-1:]
        if top in self.marks.keys():
            return self.marks[top]
        elif None in self.marks.keys():
            return self.marks[None]
        else:
            return None


class PUSH(Instruction):
    """
    PUSH-Befehl
    Syntax: PUSH reg_nr char
    """

    def __init__(self, src, reg_nr, char):
        super().__init__(src)
        self.reg_nr = reg_nr
        self.char = char

    def evaluate(self, registers, context):
        registers[context[self.reg_nr]] += self.char


class STOP(Instruction):
    """
    Stop-Befehl
    Syntax: STOP
    """

    def __init__(self, src):
        super().__init__(src)

    def evaluate(self, registers, context):
        return ()


class GOTO(Instruction):
    """
    GOTO-Befehl
    Syntax: GOTO marke
    """

    def __init__(self, src, mark):
        super().__init__(src)
        self.mark = mark

    def evaluate(self, registers, context):
        return self.mark


class NOP(Instruction):
    """ 
    Leere Instruktion: tut nichts
    """

    def __init__(self, src=""):
        super().__init__(src)

    def evaluate(self, registers, context):
        pass


@deprecated("IF_EMPTY is deprecated; use SWITCH instead")
class IF_EMPTY(Instruction):
    """
    IF_EMPTY Befehl
    Syntax: IF_EMPTY reg_nr mark
    """

    def __init__(self, src, reg_nr, goto, mark=None):
        super().__init__(src)
        self.reg_nr = reg_nr
        if mark is None:
            self.mark = goto
        else:
            if goto.upper() != "GOTO":
                raise ValueError(f"""
                Ungültiges Keyword '{goto}' in
                {self.src}
                ;\nsollte 'GOTO' sein oder weggelassen werden.""")
            self.mark = mark

    def evaluate(self, registers, context):
        if len(registers[context[self.reg_nr]]) == 0:
            return self.mark


@deprecated("IF_EQUAL is deprecated; use SWITCH instead")
class IF_EQUAL(Instruction):
    """
    IF_EQUAL Befehl
    Syntax: IF_EMPTY reg_nr mark
    """

    def __init__(self, src, reg_nr, char, goto, mark=None):
        super().__init__(src)
        self.reg_nr = reg_nr
        self.char = char
        if mark is None:
            self.mark = goto
        else:
            if goto.upper() != "GOTO":
                raise ValueError(f"""Ungültiges Keyword '{goto}' in
                {self.src};
                sollte 'GOTO' sein oder weggelassen werden.""")
            self.mark = mark

    def evaluate(self, registers, context):
        if registers[context[self.reg_nr]][-1:] == self.char:
            return self.mark


class CALL(Instruction):
    def __init__(self, src, sub_prog, *params):
        super().__init__(src)
        self.sub_prog = sub_prog
        self.params = params

    def evaluate(self, registers, context):
        return (self.sub_prog, *self.params)
