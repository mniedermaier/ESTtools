# Ghidra headless post-analysis script (Python/Jython)
# Exports a text report with functions, dangerous calls, and strings
# @category EST
# @runtime Jython

import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

DANGEROUS_FUNCS = [
    "system", "popen", "execve", "exec_cmd", "execFormatCmd",
    "sprintf", "strcpy", "strcat", "gets", "scanf", "sscanf",
    "fork", "execl"
]

CRITICAL_FUNCS = ["system", "popen", "execve", "exec_cmd", "execFormatCmd"]

STRING_PATTERNS = [
    "password", "passwd", "admin", "root", "secret",
    "login", "shell", "cmd", "/bin/", "/tmp/", "key", "token",
    "backdoor", "debug", "telnet", "tftp"
]

def get_report_path():
    args = getScriptArgs()
    if args and len(args) > 0:
        return args[0]
    return "/work/ghidra_projects/report.txt"

def write_report():
    report_path = get_report_path()
    program = currentProgram
    func_mgr = program.getFunctionManager()
    listing = program.getListing()
    sym_table = program.getSymbolTable()

    out = open(report_path, "w")

    # Header
    out.write("=" * 80 + "\n")
    out.write("  GHIDRA ANALYSIS REPORT\n")
    out.write("  Binary: %s\n" % program.getName())
    out.write("  Architecture: %s\n" % program.getLanguage().getLanguageDescription().getDescription())
    out.write("  Compiler: %s\n" % program.getCompilerSpec().getCompilerSpecDescription().getCompilerSpecName())
    out.write("  Image Base: %s\n" % program.getImageBase())
    out.write("=" * 80 + "\n\n")

    # Function summary
    functions = list(func_mgr.getFunctions(True))
    out.write("SUMMARY\n")
    out.write("-------\n")
    out.write("  Total functions: %d\n\n" % len(functions))

    # Function list
    out.write("FUNCTION LIST\n")
    out.write("-------------\n")
    out.write("  %-12s %-8s %s\n" % ("Address", "Size", "Name"))
    out.write("  %-12s %-8s %s\n" % ("-------", "----", "----"))
    for func in functions:
        size = func.getBody().getNumAddresses()
        out.write("  0x%08x  %-8d %s\n" % (func.getEntryPoint().getOffset(), size, func.getName()))
    out.write("\n")

    # Dangerous function cross-references
    out.write("DANGEROUS FUNCTION REFERENCES\n")
    out.write("-----------------------------\n")
    found_dangerous = False
    callers_to_decompile = []

    for dangerous_name in DANGEROUS_FUNCS:
        symbols = sym_table.getSymbols(dangerous_name)
        for sym in symbols:
            found_dangerous = True
            out.write("\n  [!] %s @ %s\n" % (dangerous_name, sym.getAddress()))

            refs = getReferencesTo(sym.getAddress())
            if refs:
                out.write("      Called from:\n")
                for ref in refs:
                    from_addr = ref.getFromAddress()
                    caller = func_mgr.getFunctionContaining(from_addr)
                    caller_name = caller.getName() if caller else "<unknown>"
                    out.write("        0x%08x  in %s\n" % (from_addr.getOffset(), caller_name))
                    if dangerous_name in CRITICAL_FUNCS and caller:
                        callers_to_decompile.append((caller, dangerous_name))

    if not found_dangerous:
        out.write("  None found.\n")
    out.write("\n")

    # Decompile callers of critical functions
    out.write("DECOMPILED FUNCTIONS (callers of dangerous functions)\n")
    out.write("----------------------------------------------------\n")

    decomp = DecompInterface()
    decomp.openProgram(program)
    decompiled_set = set()

    for caller, dangerous_name in callers_to_decompile:
        if caller.getEntryPoint() in decompiled_set:
            continue
        decompiled_set.add(caller.getEntryPoint())

        results = decomp.decompileFunction(caller, 30, ConsoleTaskMonitor())
        decomp_func = results.getDecompiledFunction()
        if decomp_func:
            out.write("\n  // %s @ %s\n" % (caller.getName(), caller.getEntryPoint()))
            out.write("  // Calls: %s\n" % dangerous_name)
            out.write(decomp_func.getC() + "\n")

    decomp.dispose()

    if not callers_to_decompile:
        out.write("  No callers of critical functions found to decompile.\n")
    out.write("\n")

    # Interesting strings
    out.write("INTERESTING STRINGS\n")
    out.write("-------------------\n")
    string_count = 0

    data_iter = listing.getDefinedData(True)
    while data_iter.hasNext() and string_count < 200:
        data = data_iter.next()
        dt_name = data.getDataType().getName().lower()
        if "string" in dt_name:
            value = data.getDefaultValueRepresentation()
            if value:
                lower = value.lower()
                for pattern in STRING_PATTERNS:
                    if pattern in lower:
                        out.write("  0x%08x  %s\n" % (data.getAddress().getOffset(), value))
                        string_count += 1
                        break

    if string_count == 0:
        out.write("  (No matching strings found in defined data)\n")
    out.write("\n")

    out.write("=" * 80 + "\n")
    out.write("  END OF REPORT\n")
    out.write("=" * 80 + "\n")
    out.close()

    println("Report written to: " + report_path)

write_report()
