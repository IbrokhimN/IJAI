section .data
    red     db 27,"[31m",0
    reset   db 27,"[0m",0
    clear   db 27,"[2J",27,"[H",0

    heart db "   *****     *****   ",10
          db "  *******   *******  ",10
          db " ********* ********* ",10
          db " ******************* ",10
          db "  *****************  ",10
          db "   ***************   ",10
          db "    *************    ",10
          db "     ***********     ",10
          db "      *********      ",10
          db "       *******       ",10
          db "        *****        ",10
          db "         ***         ",10
          db "          *          ",10
          db 0
    len equ $ - heart

section .text
    global _start

_start:
.loop:
    mov rax, 1
    mov rdi, 1
    mov rsi, clear
    mov rdx, 7
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, red
    mov rdx, 5
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, heart
    mov rdx, len
    syscall

    mov rax, 1
    mov rdi, 1
    mov rsi, reset
    mov rdx, 4
    syscall

    mov rax, 35
    lea rdi, [rel ts1]
    xor rsi, rsi
    syscall

    jmp .loop

section .bss
    align 8
ts1:
    dq 0
    dq 200000000
