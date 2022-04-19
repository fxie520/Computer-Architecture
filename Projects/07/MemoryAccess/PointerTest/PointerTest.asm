// push constant 3030
@3030
D=A
@SP
M=M+1
A=M-1
M=D

// pop pointer 0
@SP
AM=M-1
D=M
@THIS
M=D

// push constant 3040
@3040
D=A
@SP
M=M+1
A=M-1
M=D

// pop pointer 1
@SP
AM=M-1
D=M
@THAT
M=D

// push constant 32
@32
D=A
@SP
M=M+1
A=M-1
M=D

// pop this 2
@2
D=A
@THIS
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D

// push constant 46
@46
D=A
@SP
M=M+1
A=M-1
M=D

// pop that 6
@6
D=A
@THAT
D=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D

// push pointer 0
@THIS
D=M
@SP
M=M+1
A=M-1
M=D

// push pointer 1
@THAT
D=M
@SP
M=M+1
A=M-1
M=D

// add
@SP
AM=M-1
D=M
@SP
A=M-1
M=D+M

// push this 2
@THIS
D=M
@2
A=D+A
D=M
@SP
M=M+1
A=M-1
M=D

// sub
@SP
AM=M-1
D=M
@SP
A=M-1
M=M-D

// push that 6
@THAT
D=M
@6
A=D+A
D=M
@SP
M=M+1
A=M-1
M=D

// add
@SP
AM=M-1
D=M
@SP
A=M-1
M=D+M

