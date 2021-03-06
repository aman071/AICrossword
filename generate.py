import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # print(self.domains)
        
        for var, domain in self.domains.items():
            length=var.length
            for dom_val in domain.copy():
                if len(dom_val) != length:
                    self.domains[var].remove(dom_val)

        # print(self.domains)
        # self.revise(Variable(4, 4, 'across', 5), Variable(1, 7, 'down', 7))      #(Variable(4, 4, 'across', 5), Variable(1, 7, 'down', 7)): (3, 3) ; (Variable(4, 4, 'across', 5), Variable(2, 1, 'across', 12)): None

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap_indices=self.crossword.overlaps[x,y]

        revised=False
        if overlap_indices != None:
            domain_copy=self.domains[x].copy()
            for x_word in domain_copy:
                equal_with=0
                # print('Checking ',x_word)

                for y_word in self.domains[y]:
                    # print('with ', y_word)
                    # print(x_word[overlap_indices[0]], y_word[overlap_indices[1]])
                    if x_word[overlap_indices[0]] == y_word[overlap_indices[1]]:
                        equal_with+=1
                        break

                if equal_with==0:
                    self.domains[x].remove(x_word)
                    revised=True
                    # print('Removing', x_word)
                    # print(self.domains[x])

            # print('final', self.domains[x])

        return revised
        

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs==None:
            arcs=list(self.crossword.overlaps.keys())

        # print(arcs)

        while len(arcs)!=0:
            (x,y)=arcs.pop()

            # print(x)
            # print(y)
            # print(self.crossword.overlaps[x,y])

            if self.revise(x,y):
                if len(self.domains[x])==0:
                    return False

                # print('neighbors before discard: ', self.crossword.neighbors(x))
                # print('to discard: ', y)
                # self.crossword.neighbors(x).discard(y)
                # print(self.crossword.neighbors(x))

                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        # print('appending', neighbor)
                        arcs.append( (neighbor,x) ) 

                    # else:
                        # print('heloooooooooooooooooooooo')
                        # print(neighbor)
                        # print(y)

        print(self.domains)
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False
            if assignment[var] not in self.crossword.words:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        all_words = set()

        for var in assignment:
            if len(assignment[var]) != var.length:
                return False

            if assignment[var] not in all_words:                                                #unique words 
                all_words.add(assignment[var])
            else:
                return False
            
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i,j=self.crossword.overlaps[var, neighbor]
                    if assignment[var][i] != assignment[neighbor][j]:                       # conflict check
                        return False

        return True

            
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
