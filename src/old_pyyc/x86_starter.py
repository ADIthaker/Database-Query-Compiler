def base_starter_template(total_var):
    start_temp = f"""
.global main
main:
    pushl %ebp 
    movl %esp, %ebp 
    subl ${4 * total_var}, %esp     
        """
    
    end_temp = f""" 
    movl $0, %eax 
    movl %ebp, %esp
    popl %ebp
    ret
    """
    return start_temp, end_temp