  .org $8003

SERIAL  = $8002
ESCAPE  =   $1b
CLEAR   =   $11

EXIT_VEC = $fff8

; memory allocation:
PRINT      = $50      ; 2 bytes
BYTE_BUILD = $40      ; 1 byte
OPERANDA   = $30      ; 1 byte
OPERATOR   = $20      ; 1 byte
OPERANDB   = $10      ; 1 byte

main:
  lda #<welcome_message
  sta PRINT
  lda #>welcome_message
  sta PRINT+1
  jsr print

loop:
  jsr expression
  jmp loop

; calculate an addition or subtraction, taking input and printing output
expression:
  ; get the first number and store it in memory
  jsr get_byte
  sta OPERANDA

  lda #" "
  sta SERIAL
  
  ; get the operation type, used later
  jsr get_key
  sta OPERATOR

  lda #" "
  sta SERIAL

  ; get the second number
  jsr get_byte
  sta OPERANDB

  ; print ' = '
  lda #<equals
  sta PRINT
  lda #>equals
  sta PRINT+1
  jsr print

  ; if they chose addition, skip the next section
  lda OPERATOR
  cmp #"+"
  beq .addition

  ; find the result with subtraction
  lda OPERANDA
  sec
  sbc OPERANDB
  jmp .print
.addition:
  ; add the numbers
  lda OPERANDA
  clc
  adc OPERANDB
.print:
  ; print the result
  jsr hex_byte
  stx SERIAL
  sty SERIAL

  ; return back to the system monitor
  lda #"\n" 
  sta SERIAL
  rts

; return (in a) a single key, ignoring spaces
; modifies: a (duh)
get_key:
  lda SERIAL
  beq get_key        ; if no char was typed, check again.

  cmp #"*"           ; if star was pressed,
  beq .exit          ; exit the program
  cmp #"#"           ; if shift was pressed,
  beq .shift         ; return to the system monitor

  sta SERIAL         ; else, echo back the char.
  rts
.exit:
  lda #" "
  sta SERIAL
  jmp (EXIT_VEC)
.shift:
  lda #"?"
  sta SERIAL
.shift_wait:
  lda SERIAL
  beq .shift_wait
  ldx #"\b"
  stx SERIAL

  cmp #"a"
  bne .shift_not_a
  lda #"e"
  sta SERIAL
  rts
.shift_not_a:
  cmp #"b"
  bne .shift_not_b
  lda #"f"
  sta SERIAL
  rts
.shift_not_b
  cmp #"c"
  bne .shift_not_c
  lda #"+"
  sta SERIAL
  rts
.shift_not_c:
  cmp #"d"
  bne .shift_not_d
  lda #"-"
  sta SERIAL
  rts
.shift_not_d:
  jmp get_key ; no shift-mode key was pressed

; wait for a key and return (in a) the value of a single hex char
; modifies: a (duh)
get_nibble:
  jsr get_key
  cmp #$3a
  bcc .digit
  sec
  sbc #"a" - 10
  rts
.digit:
  sbc #"0" - 1
  rts

; return (in a) the a register as hex
; modifies: a (duh)
hex_nibble:
  cmp #10
  bcc .digit
  clc
  adc #"a" - 10
  rts
.digit:
  adc #"0"
  rts

; return (in x & y) the a register as hex
; modifies: x, y, a
hex_byte:
  pha ; save the full value for later
  ; get just the MSN
  lsr
  lsr
  lsr
  lsr
  jsr hex_nibble
  tax ; but the hex char for the MSN in x

  pla ; bring back the full value
  and #$0f ; get just the LSN
  jsr hex_nibble
  tay ; but the hex char for the LSN in y

  rts

; wait for a key and return (in a) the value of a byte (2 hex chars)
; modifies: a (duh)
get_byte:
  ; get the MS nibble and move it to the MS area of the a reg
  jsr get_nibble
  asl
  asl
  asl
  asl
  ; move the MSN to memory
  sta BYTE_BUILD

  ; get the LSN and combine it with the MSN
  jsr get_nibble
  ora BYTE_BUILD
  rts

; print a null-terminated string pointed to by PRINT
; modifies: a, y
print:
  ldy #0
.loop:
  lda (PRINT),y
  beq .done
  sta SERIAL
  iny
  jmp .loop
.done:
  rts

welcome_message:
  .byte CLEAR
  .byte "Ozpex 64 Calculator (Portable) v1.0.1\n"

  .byte "TIP: Spaces are optional.\n\n"

  .byte "Controls:\n"
  .byte "  e: #a\n"
  .byte "  f: #b\n"
  .byte "  +: #c\n"
  .byte "  -: #d\n"
  .byte "  Exit: *\n\n"

  .byte 0

equals:
  .byte " = ", 0
