.intel_syntax noprefix
.text
.globl step
step:
    push rbp
    mov rbp,rsp
    sub rsp,160
    mov QWORD PTR [rbp-8],r8
    mov QWORD PTR [rbp-152],rdx
    mov rax,QWORD PTR [rcx+0]
    mov QWORD PTR [rbp-16],rax
    mov QWORD PTR [rbp-24],0
    mov QWORD PTR [rbp-32],0
    mov QWORD PTR [rbp-40],0
    mov QWORD PTR [rbp-48],0
    lea rax,[rbp-16]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,0
    mov r10,rax
    pop rax
    cmp rax,r10
    setne al
    movzx rax,al
    test rax,rax
    jz .Lelse1
    mov rax,0
    push rax
    lea rax,[rbp-24]
    pop r10
    mov QWORD PTR [rax],r10
    jmp .Ldone1
.Lelse1:
.Ldone1:
    mov r11,QWORD PTR [rbp-152]
    mov rax,QWORD PTR [rbp-24]
    mov QWORD PTR [r11+0],rax
    mov rax,QWORD PTR [rbp-32]
    mov QWORD PTR [r11+8],rax
    mov rax,QWORD PTR [rbp-40]
    mov QWORD PTR [r11+16],rax
    mov rax,QWORD PTR [rbp-48]
    mov QWORD PTR [r11+24],rax
    leave
    ret
