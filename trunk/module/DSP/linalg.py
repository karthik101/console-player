#! python $this 

"""
    goals 
    solve det(A) for nxn matrix
    solve system Ax = b.

    Linear Algebra with applications by Otto Bretscher
    page 251 nxn determinates (recursive)
    page 283 cramers rule

    Note: for the following indexing into an array is 1-based (like Matlab) instead of from zero
            as in python or C. for the code that follows indexing will be normal.
            
    det(A) = sum(i=1,N) { (-1)^(i+1) * a_i1 * det(A_i1)  }
    
    notation:
        a_ij means value at row i and column j
        A_ij means minor of matrix A, result after deleting the ith row and jth col
             the resultant matrix will be of size N-1 x N-1.
        det(A) when A is a 1x1 matrix equals a_11.
    
    Note: in the code below a_ij equals A[i][j]. 
    A matrix is defined as an array of row vectors.
"""

def __printm(A):
    print 
    for row in A:
        print ' '.join( [ "%7.2f"%r for r in row ])

def matrix_minor(A,i,j):
    """
        return a matrix with the ith row and jth column removed.
        # unused because this is very slow.
    """
    B = [ list(row) for row in A ]
    B.pop(i)
    for row in B:
        row.pop(j)        
    return B
    
def determinate(A,N):
    """
        A as a matrix of size N x N
        Laplace expansion to define the determinate of an NxN matrix
        
        Note:
            except for N=1,2 or 3. this function has a runtime
            of O(N!). I have a fairly good machine, and for N <= 9,
            this is not so bad. N=9 takes an average of .4 seconds.
            meaning that N=10 takes 4 seconds.
    """
    
    if N == 1:
        return A[0][0]
    if N == 2:
        # a b
        # c d
        # det(A) = ad - bc
        return A[0][0]*A[1][1] - \
               A[0][1]*A[1][0] 
    if N == 3:
        # a b c 
        # d e f
        # g h i
        # det(A) = aei + bfg +cdh - ceg - bdi - afh
        return A[0][0]*A[1][1]*A[2][2] + \
               A[0][1]*A[1][2]*A[2][0] + \
               A[2][1]*A[1][1]*A[2][0] - \
               A[0][1]*A[1][0]*A[2][2] - \
               A[0][0]*A[1][2]*A[2][0] 
    
    
    total = 0
    
    for  i in xrange(N):
        c = (-1)**(i)
        a_i0 = A[i][0]
        if a_i0 != 0:
            #---------------------------------
            #A_i0 = matrix_minor(A,i,0)
            # optimization to matrix_minor as j==0
            A_i0 = [ row[1:] for row in A ]
            A_i0.pop(i)  
            #---------------------------------
            #det_A_i0 = determinate(A_i0,N-1)
            #total += c*a_i0*det_A_i0
            total += c*a_i0*determinate(A_i0,N-1)
        
    return total

def matrix_col_replace(A,b,j):
    """
        return a new matrix whose jth column
        has been replaced by a vector b.
        
        for this function b is defined as a row vector to simplify the code.
    """
    
    B = [ list(row) for row in A ]
    for i,row in enumerate(B):
        row[j] = b[i]
    return B
    
def matrix_row_swap(A,i,j):
    t = A[i]
    A[i] = A[j]
    A[j] = t
def matrix_row_mult(A,i,k):
    A[i] = [ k*item for item in A[i] ]
def matrix_row_addition(A,i,j,k=1):
    """ given a Matrix add row j to row i
        multiplies each element in i by k
        before adding.
    """
    for index,b in enumerate(A[j]):
        A[i][index] += k*b
        
def matrix_augment(A,b):
    """ return an augmented matrix
        for a linear system Ax=b
        where A is an NxN matrix and x,b are
        both column vectors of length N
        an augmented matrix is an Nx(N+1) matrix
        where each value in b is appended to the
        end of the corresponding row in A.
        
        for simplicity, b is a row-vector
        instead of a column vector.
    """
    B = [ row + [v,] for row,v in zip(A,b) ]
    return B;
 
def matrix_row_shift(A,i):
    """
        move row i to the last position
        and shift all rows up
        so that:
        A[i] = A[i+1]
        A[i+1] = A[i+2]
        and lastly:
        A[N-1] = A[i]
        implementation: use bubble sort all the way down.
    """
    for j in range(i,N-1):
        matrix_row_swap(A,j,j+1)
 
def gauss_jordan(A):
    """
        
        if A is an augmented matrix of AI, I being the identity matrix
        then the result of the function is to transform Matrix A
        into a new matrix IB where B is the inverse matrix of A.
        
        if A is an augmented matrix of Ab where b is a vector from
        Ax=b then the solution will be Ix where I is the identity matrix
        and x is the solution to the system.
        
        problems:
            if there is no solution strange things happen.
            
            1/3 - (1 - 2/3) may not equal zero.
            this floating point 'bug' is roughly solved by always
            swapping to a row that has the absolute maximum.
            the hope is some number exists that is greater than
            1E16, or some equivaltnly small value that should be zero.
        
    """
    # page 18 mentions the case where the remaining items in a column
    # are all zero, you should move to the next column but keep the same row
    # a modification (loop over cx and not cy) solved this.
    N = len(A) # specifically i want the height here as the width could be anything.
    abs_pos = -1
    abs_val = -1
    abs_tmp = -1
    cy = 0
    for cx in range(N):
        # numerical optimization, find the absolute largest value even when the value is non-zero
        #if A[c][c] == 0: # swap rows until i get a non zero entry at the cursor.
        #    for t in range(c,N):
        #        if A[t][c] != 0:
        #            matrix_row_swap(A,c,t)
        #            print "row swap %d %d"%(c,t)
        #            __printm(A)
        
        # find the absolute largest non zero row
        # swap into the cursor position
        abs_tmp = 0    
        abs_pos = -1
        abs_val = 0
        #print range(cy,N)
        for t in range(cy,N):
            abs_tmp = abs(A[t][cx])
            if abs_tmp > abs_val:
                abs_val = abs_tmp
                abs_pos = t
        if abs_val == 0:
            continue # move to next column
        if abs_pos != cy and abs_pos > 0:
            #print "row swap %d %d"%(cy,abs_pos)
            matrix_row_swap(A,cy,abs_pos)
        
        if A[cy][cx] != 0:
            #print "row mult %d by k=%f"%(cy,1.0/A[cy][cx])
            matrix_row_mult(A,cy,1.0/A[cy][cx])
            #__printm(A)
            for i in range(0,N): 
                if i == cy: continue;
                # TODO: is k=-b/a more stable than? perform row_mult after this block?
                # row addition can be optimized when the first i rows are all zero, for the current cy
                matrix_row_addition(A,i,cy,-A[i][cx])
        #__printm(A)
        cy += 1
    
    
def cramers_rule(A,b):
    """
        cramers rule is O(N*N!) - basically useless.
        gauss jordan is can be numerically unstable
        and is harder to
    """
    N = len(b)
    print "get S",N
    S = float(determinate(A,N))
    s = 1/S
    print s
    
    x = []
    for i in range(N) :
        x.append( determinate(matrix_col_replace(A,b,i),N)*s )
        print x[-1]
    
    return x;
    
def solve(A,b):
    """
        use gauss jordan elimination to solve a
        linear system of equations.
        potentially numerically unstable.
        better: LU decomposition.
        
        this function is undefined for systems with no solutions.
    """    
    B = matrix_augment(A,b)
    gauss_jordan(B)
    return [ row[-1] for row in B ]
    
"""
solutions using ref : http://www.math.hmc.edu/calculus/tutorials/linearsystems/
using Gauss-Jordon Reduction.  at the bottom of the page.

from : http://people.richland.edu/james/lecture/m116/matrices/determinant.html
Elementary Row Operations
"""
    
if __name__=="__main__":
    # the following matrix is found on page 251 for which a solution
    # is also given, making it easy to double check the above code.
    from random import randint
    import cProfile
    # A = [ [0,2,0,0,0],
    #       [0,0,0,6,0],
    #       [0,0,0,0,4],
    #       [3,0,0,0,0],
    #       [0,0,5,0,0],
    #     ]
    # A = [ [0,2,0,],
    #       [0,0,0,],
    #       [0,0,0,],
    #     ]
    #     
    # for N in range(3,11):
    #     print N
    #     B = matrix_augment(A,[ randint(-5,5) for i in range(N) ])
    #     cProfile.run("gauss_jordan(B)")
    #     __printm(B)
    #     A.append( [ randint(-5,5) for i in range(N) ] )
    #     for row in A:
    #         row.append(randint(5,5))
    
    
    # this matrix is taken from page 12, where 
    # the author goes step by step in showing the reduction chain
    # also note even though he went step by step my edition of the
    # book gives the wrong answer :(
    A = [ 
          [ 4, 10,-1,],
          [ 2,  5, 1,],
          [ 2,  8,-4,],
        ]
    print solve(A,[1,5,2])
    # problem 15 on page 20
    A = [ 
          [ 3, 5, 3],
          [ 7, 9,19],
          [-4, 5,11],
        ]
    print solve(A,[25,65,5])
    # from wikipedia, an example that, without swapping
    # for the absolute largest, produces a numerically
    # unstable system. the answer below is exactly integer 10 and 1
    A = [ 
          [ 0.003, 59.140], # step 1 divide by .003
          [ 5.291, -6.130], # step 2 subtract 5.291 *((I)) 
        ] # I'm surprised the floating point math works out
    print "Potentially unstable System solved:",solve( A, [59.17,46.78] ) == [10,1]
    import math
    pi = math.pi
    A = [ 
          [ pi*pi, pi],
          [ 4*pi*pi, 2*pi],
        ]
    
    print solve(A,[math.exp(math.pi) - 1,math.exp(2.0*math.pi) - 1])
    # [980.4205405184122, -445.92888499364756, 1.0]
    [24.834342408146526, ]
    #  24.834342408146526*x*x - 70.97178631419632*x + 1
    #  0.8416785741175774*x*x + 0.8766032543414677*x + 1
    
    