// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


//While true
(START)
@KBD
D=M

//if keyboard ==0 ->D=-1
@WHITE
D;JEQ
D=-1
@FILL
0;JMP

//else	D=0
(WHITE)
D=0

(FILL)
@color
M=D

@SCREEN
D=A
@i
M=D

//for i= screen:end:
(LOP)
@color
D=M

@i
A=M
M=D

@i
M=M+1

D=M
@8192
D=D-A
@SCREEN
D=D-A

@LOP
D;JNE

@START
0;JMP