# Ghidra headless post-analysis script (Python/Jython)
# Exports an HTML report with functions, dangerous calls, and decompiled code
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

def esc(text):
    """Escape HTML special characters"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def get_report_path():
    args = getScriptArgs()
    if args and len(args) > 0:
        return args[0]
    return "/work/reports/report.html"

def write_report():
    report_path = get_report_path()
    program = currentProgram
    func_mgr = program.getFunctionManager()
    listing = program.getListing()
    sym_table = program.getSymbolTable()

    out = open(report_path, "w")

    binary_name = esc(program.getName())
    arch = esc(program.getLanguage().getLanguageDescription().getDescription())
    compiler = esc(program.getCompilerSpec().getCompilerSpecDescription().getCompilerSpecName())
    image_base = esc(str(program.getImageBase()))

    functions = list(func_mgr.getFunctions(True))

    # HTML header
    out.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Ghidra Report - %s</title>
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; }
  h1 { color: #89b4fa; border-bottom: 2px solid #89b4fa; padding-bottom: 10px; }
  h2 { color: #f9e2af; margin-top: 30px; border-bottom: 1px solid #45475a; padding-bottom: 5px; }
  h3 { color: #a6e3a1; }
  .header-info { background: #313244; padding: 15px; border-radius: 8px; margin: 15px 0; }
  .header-info td { padding: 4px 15px 4px 0; }
  .header-info .label { color: #89b4fa; font-weight: bold; }
  .summary-box { display: inline-block; background: #313244; padding: 15px 25px; border-radius: 8px; margin: 10px 5px; text-align: center; }
  .summary-box .number { font-size: 2em; color: #89b4fa; font-weight: bold; }
  .summary-box .label { color: #a6adc8; font-size: 0.9em; }
  table { border-collapse: collapse; width: 100%%; margin: 10px 0; }
  th { background: #313244; color: #89b4fa; text-align: left; padding: 8px 12px; position: sticky; top: 0; }
  td { padding: 6px 12px; border-bottom: 1px solid #313244; }
  tr:hover { background: #313244; }
  .danger { color: #f38ba8; font-weight: bold; }
  .warn { color: #fab387; }
  .addr { color: #94e2d5; font-family: monospace; }
  .func-name { color: #a6e3a1; }
  code { background: #181825; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
  pre { background: #181825; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; line-height: 1.4; border-left: 3px solid #89b4fa; }
  .xref-list { margin: 5px 0 15px 20px; }
  .xref-item { padding: 2px 0; }
  .tag-high { background: #f38ba8; color: #1e1e2e; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold; }
  .tag-med { background: #fab387; color: #1e1e2e; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold; }
  .collapsible { cursor: pointer; user-select: none; }
  .collapsible:hover { color: #89b4fa; }
  .content { display: none; }
  .string-val { color: #a6e3a1; }
  nav { background: #313244; padding: 10px 15px; border-radius: 8px; margin: 15px 0; }
  nav a { color: #89b4fa; text-decoration: none; margin-right: 20px; }
  nav a:hover { text-decoration: underline; }
  footer { margin-top: 40px; padding-top: 15px; border-top: 1px solid #45475a; color: #6c7086; text-align: center; font-size: 0.85em; }
</style>
</head>
<body>
<h1>Ghidra Analysis Report</h1>
<nav>
  <a href="#summary">Summary</a>
  <a href="#functions">Functions</a>
  <a href="#dangerous">Dangerous References</a>
  <a href="#decompiled">Decompiled Code</a>
  <a href="#strings">Strings</a>
</nav>
<div class="header-info">
<table>
  <tr><td class="label">Binary</td><td>%s</td></tr>
  <tr><td class="label">Architecture</td><td>%s</td></tr>
  <tr><td class="label">Compiler</td><td>%s</td></tr>
  <tr><td class="label">Image Base</td><td><span class="addr">%s</span></td></tr>
</table>
</div>
""" % (binary_name, binary_name, arch, compiler, image_base))

    # Summary
    out.write('<h2 id="summary">Summary</h2>\n')
    out.write('<div class="summary-box"><div class="number">%d</div><div class="label">Functions</div></div>\n' % len(functions))

    # Count dangerous refs for summary
    danger_count = 0
    for dangerous_name in CRITICAL_FUNCS:
        symbols = sym_table.getSymbols(dangerous_name)
        for sym in symbols:
            danger_count += 1
    out.write('<div class="summary-box"><div class="number" style="color:#f38ba8">%d</div><div class="label">Critical Imports</div></div>\n' % danger_count)

    # Function list
    out.write('<h2 id="functions">Function List</h2>\n')
    out.write('<table><thead><tr><th>Address</th><th>Size</th><th>Name</th></tr></thead><tbody>\n')
    for func in functions:
        size = func.getBody().getNumAddresses()
        name = esc(func.getName())
        out.write('<tr><td class="addr">0x%08x</td><td>%d</td><td class="func-name">%s</td></tr>\n'
                  % (func.getEntryPoint().getOffset(), size, name))
    out.write('</tbody></table>\n')

    # Dangerous function cross-references
    out.write('<h2 id="dangerous">Dangerous Function References</h2>\n')
    callers_to_decompile = []

    for dangerous_name in DANGEROUS_FUNCS:
        symbols = sym_table.getSymbols(dangerous_name)
        for sym in symbols:
            is_critical = dangerous_name in CRITICAL_FUNCS
            tag = '<span class="tag-high">HIGH</span>' if is_critical else '<span class="tag-med">MEDIUM</span>'
            out.write('<h3>%s <code>%s</code> @ <span class="addr">%s</span></h3>\n'
                      % (tag, esc(dangerous_name), esc(str(sym.getAddress()))))

            refs = getReferencesTo(sym.getAddress())
            if refs:
                out.write('<div class="xref-list">\n')
                for ref in refs:
                    from_addr = ref.getFromAddress()
                    caller = func_mgr.getFunctionContaining(from_addr)
                    caller_name = caller.getName() if caller else "&lt;unknown&gt;"
                    out.write('<div class="xref-item"><span class="addr">0x%08x</span> in <span class="func-name">%s</span></div>\n'
                              % (from_addr.getOffset(), esc(caller_name)))
                    if is_critical and caller:
                        callers_to_decompile.append((caller, dangerous_name))
                out.write('</div>\n')

    # Decompile callers of critical functions
    out.write('<h2 id="decompiled">Decompiled Functions</h2>\n')
    out.write('<p>Functions that call critical APIs (system, popen, execve, exec_cmd, execFormatCmd):</p>\n')

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
            out.write('<h3><span class="func-name">%s</span> @ <span class="addr">%s</span></h3>\n'
                      % (esc(caller.getName()), esc(str(caller.getEntryPoint()))))
            out.write('<p>Calls: <code class="danger">%s</code></p>\n' % esc(dangerous_name))
            out.write('<pre>%s</pre>\n' % esc(decomp_func.getC()))

    decomp.dispose()

    if not callers_to_decompile:
        out.write('<p>No callers of critical functions found to decompile.</p>\n')

    # Interesting strings
    out.write('<h2 id="strings">Interesting Strings</h2>\n')
    out.write('<table><thead><tr><th>Address</th><th>Value</th></tr></thead><tbody>\n')
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
                        out.write('<tr><td class="addr">0x%08x</td><td class="string-val">%s</td></tr>\n'
                                  % (data.getAddress().getOffset(), esc(value)))
                        string_count += 1
                        break

    out.write('</tbody></table>\n')
    if string_count == 0:
        out.write('<p>(No matching strings found in defined data)</p>\n')

    # Footer
    out.write("""
<footer>
  Generated by EST - Embedded Security Testing<br>
  Ghidra Headless Analysis
</footer>
<script>
document.querySelectorAll('.collapsible').forEach(el => {
  el.addEventListener('click', () => {
    const content = el.nextElementSibling;
    content.style.display = content.style.display === 'block' ? 'none' : 'block';
  });
});
</script>
</body>
</html>
""")
    out.close()

    # Make report readable by host user
    import subprocess
    subprocess.call(["chmod", "644", report_path])

    println("Report written to: " + report_path)

write_report()
