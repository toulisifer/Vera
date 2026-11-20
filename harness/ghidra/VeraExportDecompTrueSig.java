// Như VeraExportDecomp.java, nhưng áp chữ ký đúng của corpus trước khi decompile (ablation M7, góp ý G1):
//   uint64_t fn_XX(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap)
// Tách lỗi do decompiler đoán sai prototype khỏi lỗi của model. Không dùng cho lượt chạy chính.
// @category VeRA

import java.io.File;
import java.io.PrintWriter;

import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FunctionDefinitionDataType;
import ghidra.program.model.data.ParameterDefinition;
import ghidra.program.model.data.ParameterDefinitionImpl;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.UnsignedLongLongDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class VeraExportDecompTrueSig extends GhidraScript {

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

        DataType u64 = UnsignedLongLongDataType.dataType;
        DataType pu8 = new PointerDataType(UnsignedCharDataType.dataType);
        FunctionDefinitionDataType sig = new FunctionDefinitionDataType(target.getName());
        sig.setReturnType(u64);
        sig.setArguments(new ParameterDefinition[] {
            new ParameterDefinitionImpl("in", pu8, null),
            new ParameterDefinitionImpl("len", u64, null),
            new ParameterDefinitionImpl("arg", u64, null),
            new ParameterDefinitionImpl("out", pu8, null),
            new ParameterDefinitionImpl("out_cap", u64, null)});
        ApplyFunctionSignatureCmd cmd = new ApplyFunctionSignatureCmd(target.getEntryPoint(), sig, SourceType.USER_DEFINED);
        if (!cmd.applyTo(currentProgram, monitor)) {
            println("VERA_FAIL áp chữ ký " + target.getName() + ": " + cmd.getStatusMsg());
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
