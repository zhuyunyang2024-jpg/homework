import json
import os
from datetime import datetime, timedelta

# ------------------------------
# New Data Structure: HashTable
# ------------------------------
class HashTable:
    def __init__(self):
        self.table = {}

    def put(self, key, value):
        self.table[key] = value

    def get(self, key):
        return self.table.get(key, None)

    def contains(self, key):
        return key in self.table

    def remove(self, key):
        if key in self.table:
            del self.table[key]

    def values(self):
        return list(self.table.values())

# ------------------------------
# Book Class
# ------------------------------
class Book:
    def __init__(self, book_id, title, author, category, is_available=True):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.category = category
        self.is_available = is_available
        self.borrower = None
        self.borrow_date = None
        self.due_date = None
        self.fine = 0.0

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "is_available": self.is_available,
            "borrower": self.borrower,
            "borrow_date": self.borrow_date.strftime("%Y-%m-%d") if self.borrow_date else None,
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else None,
            "fine": self.fine
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["category"],
            data["is_available"]
        )
        book.borrower = data["borrower"]
        book.fine = data.get("fine", 0.0)
        if data["borrow_date"]:
            book.borrow_date = datetime.strptime(data["borrow_date"], "%Y-%m-%d")
        if data.get("due_date"):
            book.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
        return book

# ------------------------------
# User Class
# ------------------------------
class User:
    def __init__(self, username, password, max_borrow=3):
        self.username = username
        self.password = password
        self.max_borrow = max_borrow
        self.borrow_count = 0

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "max_borrow": self.max_borrow,
            "borrow_count": self.borrow_count
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"], data["password"], data["max_borrow"])
        user.borrow_count = data["borrow_count"]
        return user

# ------------------------------
# Core Library System
# ------------------------------
class LibrarySystem:
    def __init__(self, data_file="library_data.json", user_file="users.json"):
        self.data_file = data_file
        self.user_file = user_file
        self.book_hash_table = HashTable()  # New Data Structure
        self.users = []
        self.current_user = None
        self.load_data()
        self.load_users()

    # ------------------------------
    # New Algorithm: Binary Search
    # ------------------------------
    def binary_search_book(self, sorted_books, target_id):
        left, right = 0, len(sorted_books) - 1
        while left <= right:
            mid = (left + right) // 2
            if sorted_books[mid].book_id == target_id:
                return sorted_books[mid]
            elif sorted_books[mid].book_id < target_id:
                left = mid + 1
            else:
                right = mid - 1
        return None

    def get_sorted_books(self):
        books = self.book_hash_table.values()
        return sorted(books, key=lambda b: b.book_id)

    # ------------------------------
    # Data Load & Save
    # ------------------------------
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        book = Book.from_dict(item)
                        self.book_hash_table.put(book.book_id, book)
            except:
                pass

    def save_data(self):
        books = [b.to_dict() for b in self.book_hash_table.values()]
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)

    def load_users(self):
        if os.path.exists(self.user_file):
            try:
                with open(self.user_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.users = [User.from_dict(d) for d in data]
            except:
                self.users = []

    def save_users(self):
        users_data = [u.to_dict() for u in self.users]
        with open(self.user_file, "w", encoding="utf-8") as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)

    # ------------------------------
    # User Functions
    # ------------------------------
    def register(self):
        print("\n===== User Register =====")
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return
        if any(u.username == username for u in self.users):
            print("Username already exists!")
            return
        password = input("Password: ").strip()
        self.users.append(User(username, password))
        self.save_users()
        print("Register successfully!")

    def login(self):
        print("\n===== User Login =====")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        for u in self.users:
            if u.username == username and u.password == password:
                self.current_user = u
                print(f"Welcome, {username}!")
                return True
        print("Invalid username or password!")
        return False

    # ------------------------------
    # Add Book (HashTable)
    # ------------------------------
    def add_book(self):
        print("\n===== Add New Book =====")
        while True:
            book_id = input("Enter book ID (empty for auto-generate): ").strip()
            if not book_id:
                book_id = f"B{len(self.book_hash_table.values()) + 1:03d}"
            if not self.book_hash_table.contains(book_id):
                break
            print("ID already exists!")
        title = input("Book title: ").strip()
        author = input("Author: ").strip()
        category = input("Category: ").strip()
        new_book = Book(book_id, title, author, category)
        self.book_hash_table.put(book_id, new_book)
        self.save_data()
        print(f"Book '{title}' added successfully!")

    # ------------------------------
    # Borrow Book (Binary Search)
    # ------------------------------
    def borrow_book(self):
        if not self.current_user:
            print("Please login first!")
            return
        if self.current_user.borrow_count >= self.current_user.max_borrow:
            print("Maximum borrow limit reached!")
            return

        print("\n===== Borrow Book =====")
        book_id = input("Book ID: ").strip()
        sorted_books = self.get_sorted_books()
        book = self.binary_search_book(sorted_books, book_id)

        if not book:
            print("Book not found!")
            return
        if not book.is_available:
            print("Book is already borrowed!")
            return

        now = datetime.now()
        book.borrow_date = now
        book.due_date = now + timedelta(days=30)
        book.is_available = False
        book.borrower = self.current_user.username
        self.current_user.borrow_count += 1
        self.save_data()
        self.save_users()
        print(f"Borrow success! Due date: {book.due_date.strftime('%Y-%m-%d')}")

    # ------------------------------
    # Return Book
    # ------------------------------
    def return_book(self):
        print("\n===== Return Book =====")
        book_id = input("Book ID: ").strip()
        sorted_books = self.get_sorted_books()
        book = self.binary_search_book(sorted_books, book_id)

        if not book or book.is_available:
            print("Cannot return this book!")
            return

        now = datetime.now()
        if now > book.due_date:
            overdue_days = (now - book.due_date).days
            fine = overdue_days * 1.0
            book.fine = fine
            print(f"Overdue {overdue_days} days, fine: {fine:.2f}")
        else:
            book.fine = 0.0
            print("On time return, no fine.")

        book.is_available = True
        book.borrower = None
        book.borrow_date = None
        book.due_date = None

        for u in self.users:
            if u.username == book.borrower:
                u.borrow_count = max(0, u.borrow_count - 1)
                break
        self.save_data()
        self.save_users()
        print("Return successfully!")

    # ------------------------------
    # View All Books
    # ------------------------------
    def view_all_books(self):
        print("\n===== Book List =====")
        books = self.book_hash_table.values()
        if not books:
            print("No books available.")
            return
        print(f"{'ID':<8}{'Title':<20}{'Author':<12}{'Status':<10}{'Due Date':<12}{'Fine':<8}")
        print("-" * 70)
        for b in books:
            status = "Available" if b.is_available else "Borrowed"
            due = b.due_date.strftime("%m-%d") if b.due_date else "-"
            fine = f"{b.fine:.1f}" if b.fine > 0 else "-"
            print(f"{b.book_id:<8}{b.title:<20}{b.author:<12}{status:<10}{due:<12}{fine:<8}")

    # ------------------------------
    # Search Book
    # ------------------------------
    def search_book(self):
        print("\n===== Search Book =====")
        kw = input("Keyword: ").lower()
        books = self.book_hash_table.values()
        res = [b for b in books if kw in b.title.lower() or kw in b.author.lower() or kw in b.category.lower()]
        if not res:
            print("No matching books.")
            return
        for b in res:
            print(f"{b.book_id} '{b.title}' {b.author} | {'Available' if b.is_available else 'Borrowed'}")

    # ------------------------------
    # Overdue Books
    # ------------------------------
    def view_overdue(self):
        print("\n===== Overdue Books =====")
        now = datetime.now()
        books = self.book_hash_table.values()
        count = 0
        for b in books:
            if not b.is_available and b.due_date and now > b.due_date:
                days = (now - b.due_date).days
                print(f"{b.book_id} '{b.title}' | Borrower: {b.borrower} | Overdue: {days}d | Fine: {b.fine:.1f}")
                count += 1
        print(f"Total overdue: {count}")

    # ------------------------------
    # Statistics
    # ------------------------------
    def statistics(self):
        books = self.book_hash_table.values()
        total = len(books)
        available = sum(1 for b in books if b.is_available)
        borrowed = total - available
        print("\n===== Statistics Report =====")
        print(f"Total books: {total}")
        print(f"Available: {available}")
        print(f"Borrowed: {borrowed}")
        print(f"Total users: {len(self.users)}")

    # ------------------------------
    # Menu
    # ------------------------------
    def show_menu(self):
        print("\n========== Task2 Library System ==========")
        print("1. Register   2. Login      3. Add Book")
        print("4. Borrow     5. Return     6. Book List")
        print("7. Search     8. Overdue    9. Statistic  0. Exit")

# ------------------------------
# Main
# ------------------------------
def main():
    lib = LibrarySystem()
    while True:
        lib.show_menu()
        choice = input("Please select: ").strip()
        if choice == "1": lib.register()
        elif choice == "2": lib.login()
        elif choice == "3": lib.add_book()
        elif choice == "4": lib.borrow_book()
        elif choice == "5": lib.return_book()
        elif choice == "6": lib.view_all_books()
        elif choice == "7": lib.search_book()
        elif choice == "8": lib.view_overdue()
        elif choice == "9": lib.statistics()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid input")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
        for u in self.users:
            if u.username == book.borrower:
                u.borrow_count = max(0, u.borrow_count - 1)
                break
        self.save_data()
        self.save_users()
        print("Return successfully!")

    def view_all_books(self):
        print("\n===== Book List =====")
        if not self.books:
            print("No books available")
            return
        print(f"{'ID':<8}{'Title':<20}{'Author':<12}{'Status':<10}{'Due Date':<12}{'Fine':<8}")
        print("-"*70)
        for b in self.books:
            status = "Available" if b.is_available else "Borrowed"
            due = b.due_date.strftime("%m-%d") if b.due_date else "-"
            fine = f"{b.fine:.1f}" if b.fine > 0 else "-"
            print(f"{b.book_id:<8}{b.title:<20}{b.author:<12}{status:<10}{due:<12}{fine:<8}")

    def search_book(self):
        print("\n===== Search Book =====")
        kw = input("Keyword: ").lower()
        res = [b for b in self.books if kw in b.title.lower() or kw in b.author.lower() or kw in b.category.lower()]
        if not res:
            print("No matching books found")
            return
        for b in res:
            print(f"{b.book_id} 《{b.title}》 {b.author} | {'Available' if b.is_available else 'Borrowed'}")

    def view_overdue(self):
        print("\n===== Overdue Books =====")
        now = datetime.now()
        count = 0
        for b in self.books:
            if not b.is_available and b.due_date and now > b.due_date:
                days = (now - b.due_date).days
                print(f"{b.book_id} 《{b.title}》 Borrower: {b.borrower} Overdue {days}d Fine: {b.fine:.1f}")
                count +=1
        print(f"Total overdue books: {count}")

    def statistics(self):
        total = len(self.books)
        available = sum(1 for b in self.books if b.is_available)
        borrowed = total - available
        print("\n===== Statistics Report =====")
        print(f"Total books: {total}")
        print(f"Available: {available}")
        print(f"Borrowed: {borrowed}")
        print(f"Total users: {len(self.users)}")

    def show_menu(self):
        print("\n========== Task2 Library Management System ==========")
        print("1. Register   2. Login      3. Add Book")
        print("4. Borrow     5. Return     6. Book List")
        print("7. Search     8. Overdue    9. Statistics   0. Exit")

def main():
    lib = LibrarySystem()
    while True:
        lib.show_menu()
        c = input("Please select: ").strip()
        if c == "1": lib.register()
        elif c == "2": lib.login()
        elif c == "3": lib.add_book()
        elif c == "4": lib.borrow_book()
        elif c == "5": lib.return_book()
        elif c == "6": lib.view_all_books()
        elif c == "7": lib.search_book()
        elif c == "8": lib.view_overdue()
        elif c == "9": lib.statistics()
        elif c == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid input")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()