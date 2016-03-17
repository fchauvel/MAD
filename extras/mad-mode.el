;; A simple emacs-mode to edit MAD files

(defvar mad-mode-hook nil)

(defvar mad-mode-map
  (let ((map (make-keymap)))
    (define-key map "\C-j" 'newline-and-indent)
    map)
  "Keymap for MAD major mode")

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.mad\\'" . mad-mode))

(defvar mad-structure
  (regexp-opt (list "service" "operation" "client") t))

(defvar mad-actions
  (regexp-opt '("think" "query") t))


(defvar mad-font-lock-structure
  (list 
   `(,(concat "\\<" mad-structure "\\>") . font-lock-builtin-face)
   `(,(concat "\\<" mad-actions "\\>") . font-lock-constant-face))
  "Minimal highlighting expressions for MAD mode")

(defvar mad-font-lock-keywords 
  mad-font-lock-structure
  "Default highlighting expressions for MAD mode") 

(defun mad-indent-line 
  "Indent a single line of MAD simulation"
  (beginning-of-line)
  (cond 
   ((bopb) (indent-line-to 0))
   ((looking-at "^[ \t]*\\(service\\|client\\)") (indent-line to (1 * default-tab-width)))
   ((looking-at "^[ \t]*operation") (indent-line to (2 * default-tab-width)))
   ))


(defvar mad-mode-syntax-table
  (let ((table (make-syntax-table)))
    (modify-syntax-entry ?_ "w" table)
    (modify-syntax-entry ?\# "<" table)
    (modify-syntax-entry ?\n ">" table)
    table)
  "Syntax table for mad-mode")

(defun mad-mode ()
  "Major mode for editing MAD simulation files"
  (interactive)
  (kill-all-local-variables)
  (set-syntax-table mad-mode-syntax-table)
  (use-local-map mad-mode-map)
  (set (make-local-variable 'font-lock-defaults) '(mad-font-lock-keywords))
  (set (make-local-variable 'indent-line-function) 'mad-indent-line)
  (setq major-mode 'mad-mode)
  (setq mode-name "MAD")
  (run-hooks 'mad-mode-hook))

(provide 'mad-mode)
