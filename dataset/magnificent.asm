section .data
    heart db " ▄▄▄     ▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄ ",10
          db "█   █   █   █       █   █",10
          db "█   █   █   █   ▄   █   █",10
          db "█   █▄  █   █  █▄█  █   █",10
          db "█   █ █▄█   █       █   █",10
          db "█   █       █   ▄   █   █",10
          db "█▄▄▄█▄▄▄▄▄▄▄█▄▄█ █▄▄█▄▄▄█",10
          db 0
    len equ $ - heart

section .text
    global _start
_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, heart
    mov rdx, len
    syscall
    mov rax, 60
    xor rdi, rdi
    syscall
