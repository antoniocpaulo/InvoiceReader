import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'Leitor_Faturas'))

from Leitor_Faturas import app


if __name__ == "__main__":
    app.mainloop()
