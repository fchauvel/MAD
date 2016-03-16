;; A simple emacs-mode to edit MAD files

(defvar mad-mode-hook nil)

(defvar mad-mode-map
  (let ((map (make-keymap)))
    (define-key map "\C-j" 'newline-and-indent)
    map)
  "Keymap for MAD major mode")

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.mad\\'" . mad-mode))

(defvar mad-keywords 
  (regexp-opt (list "service" "operation" "client") t))

(defconst mad-font-lock-keywords-1
  (list 
   '("\\<\\(service\\|client\\|operation)\\>" . font-lock-builtin-face)
   '("\\('\\w*'\\)" . font-lock-variable-name-face))
  "Minimal highlighting expressions for MAD mode")

(defvar mad-font-lock-keywords 
  mad-font-lock-keywords-1
  "Default highlighting expressions for MAD mode") 

(defvar mad-mode-syntax-table
  (let ((st (make-syntax-table)))
    (modify-syntax-entry ?_ "w" st)
    (modify-syntax-entry ?\n "> b" st)
    st)
  "Syntax table for mad-mode")

(defun mad-mode ()
  "Major mode for editing MAD simulation files"
  (interactive)
  ;;(kill-all-local-variables)
  (set-syntax-table mad-mode-syntax-table)
  (use-local-map mad-mode-map)
  (set (make-local-variable 'font-lock-defaults) '(mad-font-lock-keywords))
  ;; (set (make-local-variable 'indent-line-function) 'mad-indent-line)  
  (setq major-mode 'mad-mode)
  (setq mode-name "MAD")
  (run-hooks 'mad-mode-hook))

(provide 'mad-mode)

;; test. my-math-mode, my first major mode

(setq my-highlights
      '(("service\\|client\\|operation" . font-lock-function-name-face)
        ("think\\|query" . font-lock-constant-face)))

(define-derived-mode mad2-mode python-mode
  (setq font-lock-defaults '(my-highlights))
  (setq mode-name "MAD"))
