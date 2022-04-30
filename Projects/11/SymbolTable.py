# Models a class-level or subroutine_level symbol table
class SymbolTable:
    def __init__(self, field_var_counter: int = 0, static_var_counter: int = 0,
                 arg_var_counter: int = 0, local_var_counter: int = 0):
        self.field_var_counter: int = field_var_counter
        self.static_var_counter: int = static_var_counter
        self.arg_var_counter: int = arg_var_counter
        self.local_var_counter: int = local_var_counter
        self.symbol_table = dict()

    def add_var(self, var_name: str, var_type: str, var_kind: str):
        assert var_kind in {"field", "static", "argument", "local"}
        if var_kind == "field":
            var_count = self.field_var_counter
            self.field_var_counter += 1
        elif var_kind == "static":
            var_count = self.static_var_counter
            self.static_var_counter += 1
        elif var_kind == "argument":
            var_count = self.arg_var_counter
            self.arg_var_counter += 1
        else:
            var_count = self.local_var_counter
            self.local_var_counter += 1

        assert var_name not in self.symbol_table
        # Each variable in the table is a dictionary
        self.symbol_table[var_name] = {"type": var_type, "kind": var_kind, "count": var_count}

    def reset(self):
        self.field_var_counter: int = 0
        self.static_var_counter: int = 0
        self.arg_var_counter: int = 0
        self.local_var_counter: int = 0
        self.symbol_table = dict()
