
@R14
D=M
@i
M=0
    
//for (i = 0; i < n-1; i++) 
(FORI) 

@R15
D=M
D=D-1
@i
D=D-M
@END
D;JLE

@j
M=0
/////for (j = 0; j < n-i-1; j++)
(FORJ)
@R15
D=M
D=D-1
@j
D=D-M
@i
D=D-M
@ENDJ
D;JLE

/////////swap

@R14
D=M
@j
M=M+D
A=M
D=M
A=A+1
D=D-M
@ESWAP
D;JGE

@j
A=M
D=M
@swap
M=D

@j
A=M
A=A+1
D=M

@j
A=M
M=D

@swap
D=M
@j
A=M
A=A+1
M=D

(ESWAP)
@R14
D=M
@j
M=M-D


/////
@j
M=M+1
@FORJ
0;JMP
(ENDJ)
@i
M=M+1
@FORI
0;JMP
(END)
@END
0;JMP


