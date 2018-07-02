import pkgutil

COMMANDS = {}
COMMANDS_HIDDEN = {}
COMMANDS_ALL = {}
__all__ = []

# Dynamically load all submodules in package
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)    
    exec('%s = module' % module_name)

    COMMANDS_ALL[module_name] = module.command
    
    if module.public:
        COMMANDS[module_name] = module.command
    else:
        COMMANDS_HIDDEN[module_name] = module.command    
    
    
