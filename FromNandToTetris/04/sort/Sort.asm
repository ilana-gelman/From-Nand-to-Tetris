// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

// Put your code here.
// BUG ---FIX ME--- OUTER_LOOP goto END 
// initialization
	
// initialization
	
	// i = R14 ( start address of the array)
	@R14
	D = M
	@i
	M = D
	
	//n = R14 + R15 (Array length)
	@R15
	D = D + M
	@n
	M = D

	(OUTER_LOOP)
	//i - n + 2> 0  -> break condition
		@i
		D = M
		@n
		D = D - M
		@2
		D = D + A
		@END
		D;JGT
		
	// inner initialization
		// j = R14
		@R14
		D = M
		@j
		M = D
		
		(INNER_LOOP)
			// j - n + 2 > 0  -> break condition
			@j
			D = M
			@n
			D = D - M
			@2
			D = D + A
			@END_INNER_LOOP
			D;JGT

		// j_plus_one = j + 1 (address of R14 + j + 1)
			@j
			D = M + 1
			@j_plus_one
			M = D
				
		// A[J] - (A[j + 1]) < 0 goto SWAP else goto CONTINUE
			@j
			A = M		
			D = M
		// [1,2] -> D = 1
			@j_plus_one
			A = M
			D = D - M
		// [1,2] -> D = 1 - 2 = -1
			@SWAP
			D;JLT
			
			(CONTINUE)
			@j
			M = M + 1
			@INNER_LOOP
			0;JMP
		
		// else i++ and goto OUTER_LOOP
		(END_INNER_LOOP)
		@n
		M = M - 1
		@OUTER_LOOP
		0;JMP
	
	(SWAP)
	//  first_value <- A[j] 
		@j
		A = M
		D = M
		@first_value
		M = D
		
	//  second_value <- A[j+1]	
		@j_plus_one
		A = M
		D = M
		@second_value
		M = D
	
	// A[j+1] = first_value
		@first_value
		D = M
		@j_plus_one // 
		A = M
		M = D
		
	// 	A[j] = second_value
		@second_value
		D = M
		@j
		A = M
		M = D
		
	// continue inner loop	
		@CONTINUE
		0;JMP
		
(END)
	@END
	0;JMP	

	
		