// Xuất pseudocode của hàm fn_XX trong chương trình đang phân tích.
// Dùng bởi vera/extract/ghidra.py qua analyzeHeadless -postScript VeraExportDecomp.java <out_dir>
// Ghi <out_dir>/<fn_XX>.c; in "VERA_OK <fn>" hoặc "VERA_FAIL <lý do>" để driver đọc.
// @category VeRA

import java.io.File;
import java.io.PrintWriter;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;

public class VeraExportDecomp extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("VERA_FAIL thiếu tham số out_dir");
            return;
        }
        File outDir = new File(args[0]);
        outDir.mkdirs();

        Function target = null;
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (f.getName().matches("fn_\\d\\d") && !f.isExternal() && !f.isThunk()) {
                target = f;
            }
        }
        if (target == null) {
            println("VERA_FAIL không thấy fn_XX trong " + currentProgram.getName());
            return;
        }

        DecompInterface di = new DecompInterface();
        di.setOptions(new DecompileOptions());
        di.toggleCCode(true);
        di.toggleSyntaxTree(false);
        if (!di.openProgram(currentProgram)) {
            println("VERA_FAIL decompiler: " + di.getLastMessage());
            return;
        }
        DecompileResults r = di.decompileFunction(target, 120, monitor);
        if (!r.decompileCompleted() || r.getDecompiledFunction() == null) {
            println("VERA_FAIL decompile " + target.getName() + ": " + r.getErrorMessage());
            di.dispose();
            return;
        }
        File out = new File(outDir, target.getName() + ".c");
        try (PrintWriter w = new PrintWriter(out, "UTF-8")) {
            w.print(r.getDecompiledFunction().getC());
        }
        di.dispose();
        println("VERA_OK " + target.getName() + " " + out.getPath());
    }
}
