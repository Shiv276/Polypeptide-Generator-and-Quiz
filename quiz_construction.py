from project import main
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from rdkit.Chem.Draw import rdMolDraw2D # type: ignore (Comes up as a Pylance error only because theres some sort of import error (still works) and makes code look bad)
from rdkit.Chem import rdDepictor
from rdkit import Chem
import re
import io
from tkinter import ttk

class PeptideQuiz:
    def __init__(self, num_questions, length, representation):
        self.representation = representation
        self.root = tk.Tk()

        self.root.tk.call('source', 'forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')

        self.num_questions = num_questions
        self.length = length

        self.q_index = 0
        self.score = 0
        self.current_answer = ""

        self.results = [] #Qnum, User, Answer, ✓/✗

        self.root.title("Peptide Quiz")

        #Dynamically pick frame size based on screen (fixes earlier problem on small screens)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        win_w = min(900, int(screen_w * 0.8))
        win_h = min(850, int(screen_h * 0.85))

        self.root.geometry(f"{win_w}x{win_h}")



        self.header = tk.Label(self.root, text="", font=("Arial", 12)) #Question Number and Score
        self.header.pack(padx = 5, pady=5)

        self.img_label = tk.Label(self.root) #Create a place for the molecule image to go
        self.img_label.pack(padx=5, pady=5)

        self.user_input_frame = tk.Frame(self.root) #Create a frame for user to input their answer
        self.user_input_frame.pack(padx=5, pady=5)
        ttk.Label(self.user_input_frame, text="Sequence (Single Letter Code):").grid(row=0, column=0, padx=10) #First 'column' is the word 'Sequence'
        self.user_input = tk.Entry(self.user_input_frame, width=20, font=("Arial", 12), fg="#247f4c") #Instantiate the textbox
        self.user_input.grid(row=0, column=1, padx=10) #Second 'column' is the textbox
        self.user_input.bind("<Return>", lambda e: self.submit_answer())


        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=6)

        self.submit_btn = ttk.Button(btn_frame, text="Submit", style='Accent.TButton', width=10, command=self.submit_answer)
        self.submit_btn.grid(row=0, column=0, padx=6)

        self.hint_btn = ttk.Button(btn_frame, text="Hint", style='Accent.TButton', width=10, command=self.hint)
        self.hint_btn.grid(row=0, column=1, padx=6)

        self.skip_btn = ttk.Button(btn_frame, text="Skip", style='Accent.TButton', width=10, command=self.skip)
        self.skip_btn.grid(row=0, column=2, padx=6)

        self.quit_btn = ttk.Button(btn_frame, text="Quit", style='Accent.TButton', width=10, command=self.quit_quiz)
        self.quit_btn.grid(row=0, column=3, padx=6)

        self.feedback = tk.Label(self.root, text="", font=("Arial", 12))
        self.feedback.pack(pady=0)

        self.root.config(cursor="gobbler")

        self.next_button = None
        self.next_question() #Starts the quiz
        self.root.mainloop()


    def update_header(self):
        self.header.config(text=f"Question {self.q_index}/{self.num_questions}   |   Score: {self.score}", fg="#247f4c")


    def next_question(self):
        self.root.unbind("<space>") #Unbind Space (defined later) for going to next question in the event of a wrong answer
        self.user_input.bind("<Return>", lambda e: self.submit_answer())

        if self.q_index >= self.num_questions: #Finish the quiz if the question index is equal/higher than number of questions
            self.show_results()
            return

        self.q_index += 1
        self.update_header() #Increase question number by 1 for each question

        self.user_input.delete(0, tk.END) #Remove previous answer from textbox

        seq, mol = main(self.length) #Generate peptide
        self.current_answer = seq

        if self.representation == "folded":
            Chem.rdDepictor.SetPreferCoordGen(False)
            rdDepictor.Compute2DCoords(mol)

        else:
            Chem.rdDepictor.SetPreferCoordGen(True)
            rdDepictor.Compute2DCoords(mol)


        draw_size = 450 if self.root.winfo_screenheight() < 900 else 600
        d = rdMolDraw2D.MolDraw2DCairo(draw_size, draw_size)  #Alternate lower level drawing method that allows background colour changes (unlike original Draw.Draw.MolToImage)
        opts = d.drawOptions()
        rdMolDraw2D.SetDarkMode(d) #Sets bonds to White, and overall chemical structure to be visible with a dark background (and black background)
        opts.setBackgroundColour((0.129, 0.129, 0.129))  #reset the black background to a dark-modeish grey colour
        d.DrawMolecule(mol)
        d.FinishDrawing()
        png_bytes = d.GetDrawingText()  # Raw png bytes because MolDraw2DCairo is so low level that it stores them in memory (or something like that).
        molecule_img = Image.open(io.BytesIO(png_bytes)) #Unpack the png bytes and convert to an ImageFile


        self.current_image = ImageTk.PhotoImage(molecule_img)
        self.img_label.config(image=self.current_image)

        self.user_input.config(state="normal")
        self.feedback.config(text="")
        if self.next_button is not None:
            self.next_button.destroy()
            self.next_button = None

        self.submit_btn.grid(row=0, column=0, padx=6)
        self.hint_btn.grid(row=0, column=1, padx=6)
        self.skip_btn.grid(row=0, column=2, padx=6)
        self.quit_btn.grid(row=0, column=3, padx=6)


    def submit_answer(self):
        user_answer = normalise(self.user_input.get())

        if not user_answer:
            self.feedback.config(text="Please either type an answer or Skip (Hint can be used for help)", fg="#247f4c")

        elif user_answer == self.current_answer:
            self.score += 1
            self.results.append((self.q_index, user_answer, self.current_answer, "✓"))
            self.next_question()

        else:
            self.results.append((self.q_index, user_answer, self.current_answer, "✗"))
            self.submit_btn.grid_forget()
            self.hint_btn.grid_forget()
            self.skip_btn.grid_forget()
            self.quit_btn.grid_forget()

            self.feedback.config(text=f"Incorrect :(\nYour Answer: {user_answer}\nCorrect Answer: {self.current_answer}", fg="#247f4c")
            self.user_input.delete(0, tk.END)
            self.user_input.config(state="disabled")
            self.next_button = ttk.Button(self.user_input_frame, text="Next Question (Spacebar)", style='Accent.TButton', command=self.next_question)
            self.next_button.grid(row=0, column=2)
            self.root.bind("<space>", lambda e: self.next_question()) #Bind Spacebar to for ease of user
            self.user_input.unbind("<Return>") #Unbind return temporarily so feedback message cant be removed accidentally by user

    def show_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Results")
        results_window.geometry("500x300")
        self.finalscore = tk.Label(results_window, text=f"Final score: {self.score}/{self.num_questions}", font=("Arial", 16), fg="#247f4c")
        self.finalscore.pack(padx=10, pady=10)

        self.results_header = tk.Label(results_window, text="Review (✓/✗ | Q# | You | Answer):", font=("Arial", 12), fg="#247f4c")
        self.results_header.pack()

        box = tk.Text(results_window, font=("Arial", 10, 'bold'), fg="#247f4c", width=300, height=11,)
        box.pack()

        for qnum, user, ans, rightORwrong in self.results:
            box.insert(tk.END, f"Q{qnum}: {rightORwrong} | Your Answer: {user} | Correct Answer: {ans}\n")
        box.config(state="disabled")

        self.user_input.unbind("<Return>")
        self.submit_btn.config(state="disabled")
        self.hint_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        self.quit_btn.config(state="disabled")
        self.user_input.config(state="disabled")
        self.feedback.config(text="Quiz finished. See Results window.") #Prevents more answering in the main window after quiz

        quit_btn_frame = tk.Frame(results_window)
        quit_btn_frame.pack()
        quit_results_btn = ttk.Button(quit_btn_frame, text="Close Quiz", style='Accent.TButton', command=self.root.destroy)
        quit_results_btn.grid(row=0, column=0)


    def hint(self):
        self.feedback.config(text = f"N-terminal residue is {self.current_answer[0]} and C-terminal residue is {self.current_answer[-1]}", fg="#247f4c")

    def skip(self):
        self.results.append((self.q_index, "(Skipped)", self.current_answer, "✗"))
        self.next_question()

    def quit_quiz(self):
        if messagebox.askyesno(title="Quit?", message = "Quit the quiz and see results?"):
            self.show_results()



def normalise(seq):
    seq = seq.strip().upper()
    seq = re.sub(r"[\s*]", "", seq) #Incase user has spaces between AA input
    return seq

def run_quiz_gui(num_questions: int, length: int, representation: str):
    PeptideQuiz(num_questions, length, representation)






class LaunchQuiz:
    """
    Shows a menu screen where the user can choose their preferred molecular representation
    and mode (length of poly-peptide)
    """
    def __init__(self):
        self.root = tk.Tk()

        self.icon = tk.PhotoImage(file='images/icon.png')
        self.root.iconphoto(True, self.icon)

        self.root.tk.call('source', 'forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')

        self.root.title("Peptide Quiz Setup")
        

        #Dynamically set frame size (fixes earlier problem on smaller screens)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        win_w = min(1400, int(screen_w * 0.9))
        win_h = min(850, int(screen_h * 0.9))

        self.root.geometry(f"{win_w}x{win_h}")




        self.root.config(cursor="gobbler")


        #Initialise representation and length options
        self.selected_representation = None
        self.selected_length = None


        #Initialise buttons so we can highlight selected one
        self.representation_buttons = {}
        self.difficulty_buttons = {}

        #Header
        self.header = tk.Label(
            self.root,
            text="Quiz Setup",
            font=("Arial", 20, "bold"),
            fg="#247f4c"
        )
        self.header.pack(pady=(15, 10))

        self.subheader = tk.Label(
            self.root,
            text="Choose a Molecular Representation and a Difficulty, then click Start Quiz.",
            font=("Arial", 11),
            fg="#247f4c"
        )
        self.subheader.pack(pady=(0, 15))

        #Main content frame
        self.mainframe = tk.Frame(self.root)
        self.mainframe.pack(padx=20, pady=10, fill="both", expand=True)

        
        #Select representation title
        representation_title = tk.Label(self.mainframe, text="1. Select Molecular Representation", font=("Arial", 16, "bold"), fg="#247f4c")
        representation_title.pack(pady=(0, 12))


        #Set up frame to hold both representations
        representation_frame = tk.Frame(self.mainframe)
        representation_frame.pack(pady=(0, 25))

        self.left_frame = tk.Frame(representation_frame)
        self.left_frame.grid(row=0, column=0, padx=40)

        self.right_frame = tk.Frame(representation_frame)
        self.right_frame.grid(row=0, column=1, padx=40)
        #Left and Right show folded vs linear, so set up two columns with 1 row


        #Load images
        folded_img = Image.open("images/mol_folded.png")
        linear_img = Image.open("images/mol_linear.png")

        max_w = 500 if screen_w > 1400 else 380
        max_h = 300 if screen_h > 900 else 230

        folded_img.thumbnail((max_w, max_h))
        linear_img.thumbnail((max_w, max_h))

        self.folded_photo = ImageTk.PhotoImage(folded_img)
        self.linear_photo = ImageTk.PhotoImage(linear_img)




        #Folded view button and image into frame
        tk.Label(self.left_frame, text="Folded View", font=("Arial", 14, "bold"), fg="#247f4c").pack(pady=(0, 0))

        folded_img_frame = tk.Frame(self.left_frame, width=500, height=300)
        folded_img_frame.pack()
        tk.Label(folded_img_frame, image=self.folded_photo).pack()

        self.representation_buttons["folded"] = ttk.Button(self.left_frame, text="Folded View", style="Accent.TButton", command=lambda: self.select_representation("folded"))
        self.representation_buttons["folded"].pack(pady=6)


        #Linear view button and image into frame
        tk.Label(self.right_frame, text="Linear View", font=("Arial", 14, "bold"), fg="#247f4c").pack(pady=(0, 0))

        linear_img_frame = tk.Frame(self.right_frame, width=500, height=300)
        linear_img_frame.pack()
        tk.Label(linear_img_frame, image=self.linear_photo).pack()

        self.representation_buttons["Linear"] = ttk.Button(self.right_frame, text="Linear View", style="Accent.TButton", command=lambda: self.select_representation("Linear"))
        self.representation_buttons["Linear"].pack(pady=6)




        #Difficulty section
        diff_title = tk.Label(
            self.mainframe,
            text="2. Select Difficulty",
            font=("Arial", 16, "bold"),
            fg="#247f4c"
        )
        diff_title.pack(pady=(10, 10))

        diff_frame = tk.Frame(self.mainframe)
        diff_frame.pack(pady=(0, 20))

        difficulty_data = {
            "Single Amino Acid": 1,
            "Easy (3-mer)": 3,
            "Medium (5-mer)": 5,
            "Hard (10-mer)": 10,
        }

        for i, (label, length) in enumerate(difficulty_data.items()):
            btn = ttk.Button(diff_frame, text=label, style="Accent.TButton", command=lambda l=length: self.select_difficulty(l))
            btn.grid(row=0, column=i, padx=10, ipadx=10, ipady=8)
            self.difficulty_buttons[length] = btn



        #Status display + Start. Shows user their selection, and allows to start quiz
        self.status_label = tk.Label(
            self.mainframe,
            text="No representation selected | No difficulty selected",
            font=("Arial", 11, "bold"),
            fg="#247f4c"
        )
        self.status_label.pack(pady=(10, 15))

        self.start_btn = ttk.Button(
            self.mainframe,
            text="Start Quiz",
            style="Accent.TButton",
            command=self.start_quiz
        )
        self.start_btn.pack(pady=10, ipadx=20, ipady=8)

        self.root.mainloop()


    def select_representation(self, representation):
        """
        Finds selected representation and gives it a tick, then sends to update_stats() to display it.
        """
        self.selected_representation = representation

        for name, btn in self.representation_buttons.items():
            if name == representation:
                btn.config(text=f"✓ {name.title()} View")
            else:
                btn.config(text=f"{name.title()} View")

        self.update_status()


    def select_difficulty(self, length):
        """
        Finds selected difficulty and gives it a tick, then sends to update_stats() to display it.
        """
        self.selected_length = length

        labels = {
            1: "Single Amino Acid",
            3: "Easy (3-mer)",
            5: "Medium (5-mer)",
            10: "Hard (10-mer)",
        }

        for btn_length, btn in self.difficulty_buttons.items():
            if btn_length == length:
                btn.config(text=f"✓ {labels[btn_length]}")
            else:
                btn.config(text=labels[btn_length])

        self.update_status()


    def update_status(self):
        """
        Updates the bottom-text showing user which options they have selected before starting
        """
        rep_text = self.selected_representation.title() if self.selected_representation else "No representation selected"

        diff_labels = {
            1: "Single Amino Acid",
            3: "Easy (3-mer)",
            5: "Medium (5-mer)",
            10: "Hard (10-mer)",
        }
        diff_text = diff_labels[self.selected_length] if self.selected_length else "No difficulty selected"

        self.status_label.config(text=f"Representation: {rep_text} | Difficulty: {diff_text}")


    def start_quiz(self):
        """
        Starts the quiz IFF both a representation and difficulty are selected.
        Shows a warning message if one or neither are selected.
        """
        if self.selected_representation is None or self.selected_length is None:
            messagebox.showwarning(title="Selection Required", message="Please select both a molecular representation and a difficulty before starting.")
            return

        self.root.destroy()
        run_quiz_gui(10, self.selected_length, self.selected_representation)


        
if __name__ == "__main__":
    LaunchQuiz()
