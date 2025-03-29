import itertools
import time

def read_input(file_name): 
    grid = [] 
    with open(file_name, 'r') as f:
        for line in f:
            if line.strip(): # ignore empty line
                row = [cell.strip() for cell in line.split(', ')]
                grid.append(row) # add the row to the grid
    
    return grid

def write_output(file_name, grid):
    with open(file_name, 'w') as f:
        for row in grid:
            f.write(', '.join(row) + '\n')

def neighbors(i, j, rows, cols):
    neighbors_list = []
    for run_i in [-1, 0, 1]:
        for run_j in [-1, 0, 1]:

            if run_i == 0 and run_j == 0:
                continue
            
            # create neighbor cell
            neighbors_i = i + run_i
            neighbors_j = j + run_j
            
            if 0 <= neighbors_i < rows and  0 <= neighbors_j < cols:
                neighbors_list.append((neighbors_i, neighbors_j))

    return neighbors_list

def get_unknown_positions(grid):
    positions = []

    for i in range(len(grid)):
       for j in range(len(grid[0])):
            if grid[i][j] == '_':
                positions.append((i, j))
    
    return  positions

def check_constranints(grid, assignment):
    """
    hàm kiểm tra các ràng buộc của grid dựa trên assignment hiện tại.
    - duyệt qua các ô chứa chữ số, đếm số ô láng giềng đã được gán là trap (true) và số ô chưa gán
    - nếu tất cả các ô láng giềng đã được gán, tổng số trap phải dúng với clue
    - nếu chưa được gán hết, số trap đã không được vượt quá clue và tổng số trap có thể đạt được (đã gán + chưa gán) phải ít nhất bằng clue
    - trả về true nếu tất cả các ràng buộc được thoả mãn, ngược lại trả về false
    """
    
    rows = len(grid)
    cols = len(grid[0])

    for i in range(rows):
        for j in range(cols):
            if grid[i][j].isdigit(): # nếu ô có chứa số
                required = int(grid[i][j])
                neighbors_list = neighbors(i, j, rows, cols)
                count_assigned = 0
                count_unassigned = 0

                for (neighbors_i, neighbors_j) in neighbors_list: 
                    # nếu ô chưa có gán kí hiệu '_' thì không có trong assignment
                    if grid[neighbors_i][neighbors_j] == '_' and (neighbors_j, neighbors_j) not in assignment:
                        count_unassigned  += 1
                    
                    # nếu ô có gán '_' thì gán giá trị trong assigment
                    elif (neighbors_i, neighbors_j) in assignment:
                        if assignment[(neighbors_i, neighbors_j)]:
                            count_assigned  += 1    # gán giá trị true và tăng count trap

                # nếu đã gán hết các ô láng giềng nhưng tổng trap không khớp với clue
                if count_unassigned == 0 and count_assigned != required:
                    return False
                
                # nếu số trap vượt quá clue
                if count_assigned > required:
                    return False
                
                # nếu tổng số trap khả dx (đã gán + có thể gán nhỏ hơn clue)
                if count_assigned + count_unassigned < required:
                    return False
                
    return True


def brute_force_solver(grid):
    """
    hàm giải bài toán bằng phương pháp brute-force
    - lấy danh sách các vị trí chưa biết ('_')
    - duyệt qua mọi khả năng gán giá trị True(trap) hoặc False(gem) cho các ô đó
    - với mỗi cấu hình, kiểm tra rằng buộc bằng hàm check_constraints.
    - nếu tìm được cấu hình hợp lệ, cập nhật grid và trả về grid kết quả
    nếu không báo lỗi
    """ 
    unknown = get_unknown_positions(grid) 
    n = len(unknown)

    # sử dụng itertools.product để duyệt qua mọi khả năng (2^n cấu hình)
    for bits in itertools.product([True, False], repeat = n):

        # tạo assignment là dictionary: key = (i, j), value là True(trap), False(gem)
        assignment = {unknown[i] : bits[i] for i in range(n)}

        # kiểm tra nếu assignment thoả ràng buộc thì cập nhật kết quả
        if check_constranints(grid, assignment):
            
            # nếu không hợp lệ tạo bản sao của grid để cập nhật kết quả
            new_grid = [row[:] for row in grid]
            for (i, j), val in assignment.items():

                # nếu val trả về true thì gán T và false gán G
                new_grid[i][j] = 'T' if val else 'G'
            return new_grid
        
    return ValueError("Error to find result by brute-force method!!.")

def backtracking_solver(grid):
    """
    hàm giải thuật toán bằng phương pháp backtracking
    - duyệt theo các ô thứ tự chưa biết
    - với mỗi ô gián giá trị True(trap) và False(Gem) cho các ô đó
    - sau mỗi lần gián giá trị đó, chúng ta kiểm tra lại assignment hiện tại có vi phạm ràng buộc hay không
    - nếu không thì tiếp tục
    - nếu có thì quay lui và thử giá trị khác
    - nếu tìm được đáp án hợp lệ thì cập nhật grid và trả về kết quả
    - nếu không thì trả về False
    """
    unknown = get_unknown_positions(grid)
    assignment = {}
    rows = len(grid)
    cols = len(grid[0])

    def backtracking(index):
        """
        hàm đệ quy backtracking
        - index là chỉ số của ô danh sách unknown cần gán giá trị
        - nếu index = unknown => đã gán hết thành công
        """
        if index == len(unknown):
            # kiểm tra khi đã gán hết
            if check_constranints(grid, assignment):
                return True
            return False
        
        i, j = unknown[index] 

        # gán giá trị T và G vào ô
        for val in [True, False]:
            assignment[(i, j)] = val

            # kiểm tra ràng buộc sau gán.
            if check_constranints(grid, assignment):

                # nếu thoả thì đề quy vào ô tiếp theo
                if backtracking(index + 1):
                    return True
            
            # nếu không thoã thì xoá ô rồi quay lui
            del assignment[(i, j)]
        
        # nếu không có giá trị nào thoã thì trả về False
        return False
    
    # bắt đầu lại từ đầu
    if backtracking(0):

        # nếu tìm được đường đi thì sao chép và cập nhật kết quả
        new_grid = [row[:] for row in grid]
        for (i, j), val in assignment.items():
            new_grid[i][j] = 'T' if val else 'G'
        return new_grid
    
    else:
        return ValueError("Error to find result by backtracking method!!")

def compare_algorithm(grid):
    """
    hàm dùng để so sánh runtime của 2 thuật toán
    """
    start = time.perf_counter()
    solution_brute_force = brute_force_solver(grid)
    runtime_brute_force = time.perf_counter() - start

    start = time.perf_counter()
    solution_backtracking = backtracking_solver(grid)
    runtime_backtracking = time.perf_counter() - start

    return solution_brute_force, runtime_brute_force, solution_backtracking, runtime_backtracking
def main():
    input_file = "input_1.txt"
    # output_file = "output_1.txt"

    grid = read_input(input_file)

    solution_brute_force, runtime_brute_force, solution_backtracking, runtime_backtracking = compare_algorithm(grid)
    # giải bằng brute_force
    print("Solution by brute_force method: ")
    try: 
        solution_brute_force = brute_force_solver(grid)
        write_output("output_of_brute_force.txt", solution_brute_force)
        print("Run time of brute_force method is: {:.6f} second".format(runtime_brute_force))
        print("solution of brute_force is writen to output_of_brute_force.txt")
    except ValueError as e:
        print("brute_force method:", e)

    # giải bằng backtracking
    print("solution by backtracking method:")
    try:
        solution_bt = backtracking_solver(grid)
        write_output("output_backtracking.txt", solution_bt)  
        print("Run time of backtracing method is: {:.6f} second".format(runtime_backtracking))
        print("solution of brute_force is writen to output_backtracking.txt")
    except ValueError as e:
        print("backtracking method:", e)


if __name__ == "__main__":
    main()