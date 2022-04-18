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

// Put your code here.

@24575
D=A
@n
M=D  // n = 24575 = address of last register to turn black

(INFLOOP)
@SCREEN
D=A
@addr
M=D  // addr = 16384 = screen's base address (1st address to turn black)

@KBD
D=M  // D = scan code of key pressed
@WHITESCREEN
D;JEQ  // If no key pressed, goto white screen loop

	(BLACKSCREEN) // Black the entire screen
	@addr
	D=M
	@n
	D=D-M
	@END
	D;JGT  // If addr > n goto END

	@addr
	A=M
	M=-1  // Turn the region covered by RAM[addr] black

	@addr
	M=M+1  // addr += 1

	@BLACKSCREEN
	0;JMP  // Goto BLACKSCREEN loop

	(WHITESCREEN) // White the entire screen
	@addr
	D=M
	@n
	D=D-M
	@END
	D;JGT  // If addr > n goto END

	@addr
	A=M
	M=0  // Turn the region covered by RAM[addr] white

	@addr
	M=M+1  // addr += 1

	@WHITESCREEN
	0;JMP  // Goto WHITESCREEN loop	

(END)
@INFLOOP
0;JMP  // Jump to beginning of program to make LOOP1 infinite
	