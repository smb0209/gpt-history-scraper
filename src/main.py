import ssl

import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

import os
import sys
import threading
import tkinter as tk
import traceback
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog
from tkinter import scrolledtext
from tkinter import ttk

from openai import OpenAI, APIConnectionError


class GPTAutoHistoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GPT Auto History Tool")
        self.geometry("900x650")

        # 상단 공통 설정 영역
        self._build_settings_frame()

        # 탭 영역
        self._build_tabs()

        # 하단 로그 영역
        self._build_log_area()

        # 내부 상태
        self.stop_requested = False

    # ================== UI 빌더 ==================

    def _build_settings_frame(self):
        frame = ttk.LabelFrame(self, text="Settings")
        frame.pack(fill="x", padx=10, pady=10)

        # API Key
        ttk.Label(frame, text="OpenAI API Key:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.api_key_var, width=50).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )

        # Model
        ttk.Label(frame, text="Model:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.model_var = tk.StringVar(value="gpt-5.1")
        ttk.Entry(frame, textvariable=self.model_var, width=20).grid(
            row=0, column=3, sticky="w", padx=5, pady=5
        )
        # Debug API key button
        ttk.Button(frame, text="Debug key", command=self.debug_api_key).grid(row=0, column=4, sticky="w", padx=5,
                                                                             pady=5)

        # Full log filename
        ttk.Label(frame, text="Full log file:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.full_log_var = tk.StringVar(value="results_full.txt")
        ttk.Entry(frame, textvariable=self.full_log_var, width=40).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # Answers only filename
        ttk.Label(frame, text="Answers file:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.answers_log_var = tk.StringVar(value="results_answers.txt")
        ttk.Entry(frame, textvariable=self.answers_log_var, width=20).grid(
            row=1, column=3, sticky="w", padx=5, pady=5
        )

        # Output folder
        ttk.Label(frame, text="Output folder:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.output_dir_var = tk.StringVar(value="")
        ttk.Entry(frame, textvariable=self.output_dir_var, width=40).grid(
            row=2, column=1, sticky="w", padx=5, pady=5
        )
        ttk.Button(frame, text="Choose Folder", command=self._browse_output_dir).grid(
            row=2, column=2, columnspan=2, sticky="w", padx=0, pady=0
        )

        for i in range(5):
            frame.columnconfigure(i, weight=1)

    def _build_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tab 1: Date-based
        self.tab_date = ttk.Frame(notebook)
        notebook.add(self.tab_date, text="Date-based")

        self._build_date_tab()

    def _build_date_tab(self):
        frame = self.tab_date

        # Start / End date
        ttk.Label(frame, text="Start date (YYYY-MM-DD or MM-DD):").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.start_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.start_date_var, width=20).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )

        ttk.Label(frame, text="End date (YYYY-MM-DD or MM-DD):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.end_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.end_date_var, width=20).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # Step days
        ttk.Label(frame, text="Step (days):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.step_var = tk.StringVar(value="1")
        ttk.Entry(frame, textvariable=self.step_var, width=10).grid(
            row=2, column=1, sticky="w", padx=5, pady=5
        )

        # Date format radio
        self.date_format_var = tk.StringVar(value="MM-DD")
        ttk.Radiobutton(
            frame, text="Use MM-DD only", variable=self.date_format_var, value="MM-DD"
        ).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(
            frame, text="Use YYYY-MM-DD", variable=self.date_format_var, value="YYYY-MM-DD"
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Question template
        ttk.Label(frame, text="Question template (use {date}):").grid(
            row=4, column=0, sticky="nw", padx=5, pady=5
        )
        self.date_template_text = scrolledtext.ScrolledText(frame, width=80, height=6)
        self.date_template_text.grid(row=4, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.date_template_text.insert(
            "1.0",
            "{date}에 있었던 중요한 세계 역사 사건 3~5가지를 한국어로 bullet point로 정리해줘.",
        )

        # Run button
        run_btn = ttk.Button(frame, text="Run Date-based", command=self.run_date_based)
        run_btn.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=10)

        for i in range(4):
            frame.columnconfigure(i, weight=1)
        frame.rowconfigure(4, weight=1)

    def _build_log_area(self):
        frame = ttk.LabelFrame(self, text="Log")
        frame.pack(fill="both", expand=False, padx=10, pady=(0, 10))

        # Stop 버튼
        self.stop_button = ttk.Button(frame, text="Stop", command=self.request_stop)
        self.stop_button.pack(anchor="e", padx=5, pady=(5, 0))

        self.log_text = scrolledtext.ScrolledText(frame, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    # ================== Helper 메서드 ==================

    def log(self, msg: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def safe_log(self, msg: str):
        """Thread-safe log 호출용 래퍼"""
        self.after(0, self.log, msg)

    def request_stop(self):
        """백그라운드 작업 중단 요청"""
        self.stop_requested = True
        self.log("[*] Stop requested. 현재 실행 중인 작업이 순차적으로 종료됩니다.")

    def _browse_output_dir(self):
        """사용자가 결과 파일을 저장할 폴더를 선택하도록 하는 다이얼로그."""
        initial_dir = self._get_base_dir()
        selected = filedialog.askdirectory(
            title="Select output folder",
            initialdir=initial_dir,
        )
        if selected:
            self.output_dir_var.set(selected)
            self.safe_log(f"[INFO] Output folder set to: {selected}")

    def debug_api_key(self):
        """
        API Key 문자열 디버그용: 길이, 앞/뒤 일부, 각 문자 코드 포인트를 콘솔과 로그에 출력.
        키 전체는 로그에 남기지 않고 일부만 보여준다.
        """
        key = self.api_key_var.get()
        length = len(key)
        if length >= 8:
            preview = key[:4] + "..." + key[-4:]
        else:
            preview = key

        # 각 문자와 코드 포인트를 콘솔에 출력 (IntelliJ Run 콘솔에서 확인)
        charset_info = ", ".join(f"{repr(c)}({ord(c)})" for c in key)

        print("\n===== API KEY DEBUG INFO =====")
        print("Length:", length)
        print("Preview:", preview)
        print("Characters + Codepoints:", charset_info)
        print("================================\n")

        # 로그 영역에는 민감 정보 최소화된 내용만 남김
        self.safe_log(f"[DEBUG] API key length={length}, preview={preview}")

    def call_openai(self, prompt: str) -> str:
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get().strip() or "gpt-5.1"

        if not api_key:
            raise RuntimeError("Missing API key")

        # OpenAI 클라이언트
        client = OpenAI(
            api_key=api_key,
            timeout=30,
        )

        last_error = None
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=900,
                    temperature=0.7,
                )
                text = resp.choices[0].message.content or ""
                return text

            except APIConnectionError as e:
                last_error = e
                self.safe_log(
                    f"[ERROR] OpenAI 연결 실패, 재시도 {attempt + 1}/3: {e}"
                )

            except Exception as e:
                last_error = e
                tb = traceback.format_exc()
                self.safe_log(
                    f"[ERROR] OpenAI 호출 실패, 재시도 {attempt + 1}/3: {type(e).__name__}: {e}"
                )
                self.safe_log(tb)

        raise RuntimeError(f"OpenAI 호출 3회 실패: {last_error}")

    def _get_base_dir(self) -> str:
        """결과 파일을 저장할 기본 디렉터리를 결정.

        - 사용자가 Settings에서 Output folder를 지정했으면 그 경로를 사용
        - 지정하지 않았다면:
          * PyInstaller 실행파일일 때는 실행파일이 있는 폴더
          * 개발 중에는 main.py가 있는 폴더
        """
        # 1) 사용자가 Output folder를 지정한 경우 우선 사용
        output_var = getattr(self, "output_dir_var", None)
        if output_var is not None:
            val = output_var.get().strip()
            if val:
                return val

        # 2) 기본 동작 (기존 로직)
        if getattr(sys, "frozen", False):
            # PyInstaller로 빌드된 실행파일
            return os.path.dirname(sys.executable)
        else:
            # 일반 파이썬 실행
            return os.path.dirname(os.path.abspath(__file__))

    def append_to_files(self, header: str, body_question: str, body_answer: str):
        base_dir = self._get_base_dir()

        full_name = self.full_log_var.get().strip() or "results_full.txt"
        answers_name = self.answers_log_var.get().strip() or "results_answers.txt"

        full_path = os.path.join(base_dir, full_name)
        answers_path = os.path.join(base_dir, answers_name)

        try:
            # Full log: 질문 + 답변
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(header)
                if body_question:
                    f.write("[QUESTION]\n")
                    f.write(body_question.strip() + "\n\n")
                f.write("[ANSWER]\n")
                f.write(body_answer.strip() + "\n\n\n")

            # Answers only: 답변만
            with open(answers_path, "a", encoding="utf-8") as f:
                f.write(body_answer.strip() + "\n\n")
        except Exception as e:
            # 저장 중 에러를 로그에 남김
            try:
                self.safe_log(f"[ERROR] 파일 저장 실패: {e}")
            except Exception:
                pass

    def _parse_date(self, text: str) -> datetime:
        text = text.strip()
        # YYYY-MM-DD
        if len(text) == 10:
            return datetime.strptime(text, "%Y-%m-%d")
        # MM-DD → 내부 계산용으로 2000년 붙이기
        if len(text) == 5:
            return datetime.strptime("2000-" + text, "%Y-%m-%d")
        raise ValueError("날짜 형식이 잘못되었습니다. 예: 2024-01-01 또는 01-01")

    # ================== 실제 동작 로직 ==================

    def run_date_based(self):
        # API Key 체크 (여기서 한 번만)
        if not self.api_key_var.get().strip():
            messagebox.showerror("Error", "OpenAI API Key를 입력해 주세요.")
            return

        # Output folder 체크 (필수)
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Output folder를 선택해 주세요.")
            return
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Output folder를 만들 수 없습니다.\n\n{e}",
                )
                return

        try:
            start = self._parse_date(self.start_date_var.get())
            end = self._parse_date(self.end_date_var.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            step_days = int(self.step_var.get().strip() or "1")
            if step_days <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Step(days)는 1 이상의 정수를 입력해 주세요.")
            return

        template = self.date_template_text.get("1.0", "end").strip()
        if not template:
            messagebox.showerror("Error", "Question template을 입력해 주세요.")
            return

        date_format = self.date_format_var.get()  # "YYYY-MM-DD" or "MM-DD"

        # Stop 플래그 초기화
        self.stop_requested = False
        self.safe_log("[*] Date-based 작업 시작")

        t = threading.Thread(
            target=self._run_date_based_worker,
            args=(start, end, step_days, template, date_format),
            daemon=True,
        )
        t.start()

    def _run_date_based_worker(self, start: datetime, end: datetime, step_days: int, template: str, date_format: str):
        current = start
        while current <= end:
            if self.stop_requested:
                self.safe_log("[*] Date-based 작업이 Stop 요청에 의해 중단되었습니다.")
                break

            if date_format == "YYYY-MM-DD":
                date_str = current.strftime("%Y년 %m월 %d일")
            else:
                date_str = current.strftime("%m월 %d일")

            question = template.replace("{date}", date_str)
            self.safe_log(f"[Date] {date_str} 질문 중...")

            try:
                answer = self.call_openai(question)
            except Exception as e:
                self.safe_log(f"[ERROR] {date_str} 처리 실패: {e}")
                header = f"===== DATE: {date_str} =====\n"
                self.append_to_files(header, question, "<ERROR: failed to fetch response>")
                current += timedelta(days=step_days)
                continue

            header = f"===== DATE: {date_str} =====\n"
            self.append_to_files(header, question, answer)
            self.safe_log(f"[OK] {date_str} 저장 완료")

            current += timedelta(days=step_days)

        self.safe_log("[*] Date-based 작업 종료")


if __name__ == "__main__":
    app = GPTAutoHistoryApp()
    app.mainloop()
