// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

// Initialization
	@i
	M = 0
	@sum
	M = 0
	
// Adding R1 times R0 to sum
	
	(LOOP)
		@i
		D = M 			// D = i
		@R1 			// M = R1
		D = D - M  		// D = i - R1
		
// Break Condition	
	
		@STOP
		D;JGE
		
// Loop Body: sum = sum + R0	
	
		@sum
		D = M
		@R0
		D = D + M
		@sum
		M = D
		
// increment i 	
	
		@i
		M = M + 1

// Back to loop 	
	
		@LOOP
		0;JMP
		
// R2 = sum 
		
	(STOP)
		@sum
		D = M
		@R2
		M = D
		
//  Infinte loop		
	(END)
		@END
		0;JMP