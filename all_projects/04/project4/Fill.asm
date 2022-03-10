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

// Put your code as fllow:

    @8192
    D=A
    @n
    M=D //n = 8192

    @flag
    M=0 // @flag = 0


(BEGIN)
    //Initialize variables
    @i
    M=0 // @i = 0

    @SCREEN
    D=A
    @disp
    M=D // @disp = SCREEN

    @KBD
    D=M
    @L2B
    D;JGT   //if @KBD > 0 ; goto L2B
    @L2W
    D;JEQ   //else if @KBD == 0 ; goto L2W

(L2B)
    @flag
    D=M
    @L2BEND
    D;JGT   // if flag > 0 ; goto L2BEND

    @i
    D=M
    @n  //循环次数
    D=D-M
    @L2BEND
    D;JEQ

    @disp
    A=M
    M=-1

    @disp
    M=M+1

    @i
    M=M+1

    @L2B
    0;JMP
(L2BEND)
    @flag
    M=1
    @BEGIN
    0;JMP


(L2W)
    @flag
    D=M
    @L2WEND
    D;JEQ   // if flag == 0 ; goto L2BEND

    @i
    D=M
    @n  //循环次数
    D=D-M
    @L2WEND
    D;JEQ

    @disp
    A=M
    M=0

    @disp
    M=M+1

    @i
    M=M+1

    @L2W
    0;JMP
(L2WEND)
    @flag
    M=0
    @BEGIN
    0;JMP