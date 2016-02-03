def fetch_functions(script_filepath, regex):
    import os
    import imp
    import inspect
    import re

    script_name = os.path.basename(script_filepath)
    mod_name = os.path.splitext(script_name)[0]
    mod = imp.load_source(mod_name, script_filepath)

    funcs = []
    for func in inspect.getmembers(mod, inspect.isfunction):
        func_name = func[0]
        m = re.match(regex, func_name)
        if m:
            funcs.append(func[1])

    return funcs
