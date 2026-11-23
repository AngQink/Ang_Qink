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
    mov rax,QWORD PTR [rcx+8]
    mov QWORD PTR [rbp-24],rax
    mov rax,QWORD PTR [rcx+16]
    mov QWORD PTR [rbp-32],rax
    mov rax,QWORD PTR [rcx+24]
    mov QWORD PTR [rbp-40],rax
    mov QWORD PTR [rbp-48],0
    mov QWORD PTR [rbp-56],0
    mov QWORD PTR [rbp-64],0
    mov QWORD PTR [rbp-72],0
    mov QWORD PTR [rbp-80],0
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
    lea rax,[rbp-16]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,1
    mov r10,rax
    pop rax
    cmp rax,r10
    sete al
    movzx rax,al
    test rax,rax
    jz .Lelse2
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+0]
    mov rax,QWORD PTR [rax]
    mov r10,rax
    pop rax
    cmp rax,r10
    setg al
    movzx rax,al
    test rax,rax
    jz .Lelse3
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+256]
    mov rax,QWORD PTR [rax]
    mov r10,rax
    pop rax
    cmp rax,r10
    setg al
    movzx rax,al
    test rax,rax
    jz .Lelse4
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+256]
    pop r10
    mov QWORD PTR [rax],r10
    lea rax,[rbp-40]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+768]
    pop r10
    mov QWORD PTR [rax],r10
    mov rax,1
    push rax
    lea rax,[rbp-48]
    pop r10
    mov QWORD PTR [rax],r10
    jmp .Ldone4
.Lelse4:
.Ldone4:
    jmp .Ldone3
.Lelse3:
.Ldone3:
    jmp .Ldone2
.Lelse2:
.Ldone2:
    lea rax,[rbp-16]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,2
    mov r10,rax
    pop rax
    cmp rax,r10
    sete al
    movzx rax,al
    test rax,rax
    jz .Lelse5
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+256]
    mov rax,QWORD PTR [rax]
    mov r10,rax
    pop rax
    cmp rax,r10
    sete al
    movzx rax,al
    test rax,rax
    jz .Lelse6
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+0]
    mov rax,QWORD PTR [rax]
    mov r10,rax
    pop rax
    cmp rax,r10
    setg al
    movzx rax,al
    test rax,rax
    jz .Lelse7
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,20
    mov r10,rax
    pop rax
    imul rax,r10
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+768]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,100
    mov r10,rax
    pop rax
    add rax,r10
    push rax
    mov rax,8
    mov r10,rax
    pop rax
    imul rax,r10
    mov r10,rax
    pop rax
    add rax,r10
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,rax
    pop rax
    add rax,r10
    push rax
    mov rax,34
    mov r10,rax
    pop rax
    add rax,r10
    push rax
    mov rax,257
    mov r10,rax
    pop rax
    cqo
    idiv r10
    mov rax,rdx
    push rax
    lea rax,[rbp-80]
    pop r10
    mov QWORD PTR [rax],r10
    lea rax,[rbp-40]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-80]
    mov rax,QWORD PTR [rax]
    mov r10,rax
    pop rax
    cmp rax,r10
    sete al
    movzx rax,al
    test rax,rax
    jz .Lelse8
    lea rax,[rbp-32]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+0]
    pop r10
    mov QWORD PTR [rax],r10
    mov rax,0
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+256]
    pop r10
    mov QWORD PTR [rax],r10
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+768]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+512]
    pop r10
    mov QWORD PTR [rax],r10
    mov rax,0
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+768]
    pop r10
    mov QWORD PTR [rax],r10
    mov rax,1
    push rax
    lea rax,[rbp-48]
    pop r10
    mov QWORD PTR [rax],r10
    jmp .Ldone8
.Lelse8:
.Ldone8:
    jmp .Ldone7
.Lelse7:
.Ldone7:
    jmp .Ldone6
.Lelse6:
.Ldone6:
    jmp .Ldone5
.Lelse5:
.Ldone5:
    lea rax,[rbp-16]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,3
    mov r10,rax
    pop rax
    cmp rax,r10
    sete al
    movzx rax,al
    test rax,rax
    jz .Lelse9
    mov rax,0
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+256]
    pop r10
    mov QWORD PTR [rax],r10
    mov rax,0
    push rax
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+768]
    pop r10
    mov QWORD PTR [rax],r10
    mov rax,2
    push rax
    lea rax,[rbp-48]
    pop r10
    mov QWORD PTR [rax],r10
    jmp .Ldone9
.Lelse9:
.Ldone9:
    lea rax,[rbp-16]
    mov rax,QWORD PTR [rax]
    push rax
    mov rax,4
    mov r10,rax
    pop rax
    cmp rax,r10
    sete al
    movzx rax,al
    test rax,rax
    jz .Lelse10
    mov rax,3
    push rax
    lea rax,[rbp-48]
    pop r10
    mov QWORD PTR [rax],r10
    jmp .Ldone10
.Lelse10:
.Ldone10:
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+0]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-56]
    pop r10
    mov QWORD PTR [rax],r10
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+512]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-64]
    pop r10
    mov QWORD PTR [rax],r10
    lea rax,[rbp-24]
    mov rax,QWORD PTR [rax]
    mov r10,QWORD PTR [rbp-8]
    lea rax,[r10+rax*8+256]
    mov rax,QWORD PTR [rax]
    push rax
    lea rax,[rbp-72]
    pop r10
    mov QWORD PTR [rax],r10
    jmp .Ldone1
.Lelse1:
.Ldone1:
    mov r11,QWORD PTR [rbp-152]
    mov rax,QWORD PTR [rbp-48]
    mov QWORD PTR [r11+0],rax
    mov rax,QWORD PTR [rbp-56]
    mov QWORD PTR [r11+8],rax
    mov rax,QWORD PTR [rbp-64]
    mov QWORD PTR [r11+16],rax
    mov rax,QWORD PTR [rbp-72]
    mov QWORD PTR [r11+24],rax
    leave
    ret
