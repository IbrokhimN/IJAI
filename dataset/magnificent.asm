section .data
    clear   db 27,"[2J",27,"[H",0
    center  db 27,"[10;30H",0

    color1  db 27,"[31;1m",0   ; ярко-красный (bold)
    color2  db 27,"[31m",0     ; обычный красный
    color3  db 27,"[90m",0     ; серый (затухание)
    reset   db 27,"[0m",0

    heart1 db "   ***     ***   ",10
           db " *****   *****  ",10
           db "****************",10
           db " ************** ",10
           db "  ************  ",10
           db "   **********   ",10
           db "    ********    ",10
           db "     ******     ",10
           db "      ****      ",10
           db "       **       ",10
           db 0
    len1 equ $ - heart1

    heart2 db "   *****     *****   ",10
           db "  *******   *******  ",10
           db " ******************* ",10
           db "*********************",10
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
    len2 equ $ - heart2

section .text
    global _start

_start:
.loop:
    ; ярко-красный + маленькое сердце
    mov rax,1
    mov rdi,1
    mov rsi,clear
    mov rdx,7
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,center
    mov rdx,7
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,color1
    mov rdx,6
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,heart1
    mov rdx,len1
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,reset
    mov rdx,4
    syscall

    mov rax,35
    lea rdi,[rel ts1]
    xor rsi,rsi
    syscall

    ; обычный красный + большое сердце
    mov rax,1
    mov rdi,1
    mov rsi,clear
    mov rdx,7
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,center
    mov rdx,7
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,color2
    mov rdx,5
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,heart2
    mov rdx,len2
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,reset
    mov rdx,4
    syscall

    mov rax,35
    lea rdi,[rel ts2]
    xor rsi,rsi
    syscall

    ; затухающее серое + маленькое сердце
    mov rax,1
    mov rdi,1
    mov rsi,clear
    mov rdx,7
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,center
    mov rdx,7
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,color3
    mov rdx,5
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,heart1
    mov rdx,len1
    syscall

    mov rax,1
    mov rdi,1
    mov rsi,reset
    mov rdx,4
    syscall

    mov rax,35
    lea rdi,[rel ts3]
    xor rsi,rsi
    syscall

    jmp .loop

section .bss
    align 8
ts1: dq 0,150000000
ts2: dq 0,150000000
ts3: dq 0,150000000
