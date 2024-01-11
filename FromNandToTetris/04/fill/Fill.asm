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

(LOOP)
// set i = SCREEN 16384  
	@SCREEN
	D = A
	@i
	M = D

// Setting Keyboard 
	@KBD
	D = M
	
// set color to black if KBD != 0 
	@cur
	M = 0
	@SETBLACK
	D;JNE
	
(PAINT)
// Checking if (i > 24575) 
	@i
	D=M
	@24575
	D=D-A
	@LOOP
	D;JGT	

// set *i = cur	
	@cur 
	D = M
	@i 
	A = M 
	M = D 
// increment i and goto PAINT 
	@i
	M = M +1
	@PAINT
	0;JMP

// set cur = -1 	
(SETBLACK)
	@cur
	M = -1
	@PAINT
	0;JMP


	
