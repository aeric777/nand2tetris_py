// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code as flllow:
    @R0
    D=M //D=RAM[0]
    @num0
    M=D //RAM[num0]=RAM[0]

    @R1
    D=M //D=RAM[1]
    @num1   //LOOP times : num1
    M=D //RAM[num1]=RAM[1]

    @R2
    M=0 //RAM[2]=0

    @i
    M=0

(LOOP)
    @i
    D=M
    @num1
    D=D-M
    @END
    D;JEQ

    @num0
    D=M
    @R2
    M=M+D   //RAM[R2]=RAM[R2]+num0

    @i
    M=M+1   //i++

    @LOOP
    0;JMP
(END)
    @END
    0;JMP



