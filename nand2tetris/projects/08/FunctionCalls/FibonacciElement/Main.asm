@256
D=A
@SP
M=D
@return.1
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@5
D=D-M
@0
D=D-M
@SP
D=M
@LCL
M=D
@func.Sys.init
0;JMP
(return.1)// C_PUSH argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
A=M-1
D=M
A=A-1
D=D-M
@false.gt.1
D;JLE
@SP
A=M-1
A=A-1
M=-1
@true.gt.1
0;JMP
(false.gt.1)
@SP
A=M-1
A=A-1
M=0
(true.gt.1)
@SP
M=M-1
@SP
AM=M-1
D=M
@label.IF_TRUE
D;JNE
@label.IF_FALSE
0;JMP
(label.IF_TRUE)
// C_PUSH argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
(label.IF_FALSE)
// C_PUSH argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
A=M-1
D=-M
A=A-1
M=D+M
@SP
M=M-1
// C_PUSH argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
A=M-1
D=-M
A=A-1
M=D+M
@SP
M=M-1
// add
@SP
A=M-1
D=M
A=A-1
M=D+M
@SP
M=M-1
@LCL
D=A
@endFrame
M=D
@5
D=D-A
@retAddr
M=D
@ARG
D=M
@0
D=D+A
@SP
A=M
M=D
A=A-1
D=M
A=A+1
A=M
M=D
@SP
M=M-1

@ARG
D=A+1
@SP
M=D
@LCL
AM=M-1
D=M
@THAT
M=D
@LCL
AM=M-1
D=M
@THIS
M=D
@LCL
AM=M-1
D=M
@ARG
M=D
@LCL
AM=M-1
D=M
@LCL
M=D
@retAddr
0;JMP
