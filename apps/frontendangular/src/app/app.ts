import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private http = inject(HttpClient);
  
  messages = signal<Message[]>([]);
  prompt = signal('');
  loading = signal(false);

  sendMessage() {
    if (!this.prompt().trim() || this.loading()) return;
    
    const userMessage = this.prompt();
    this.messages.update(m => [...m, { role: 'user', content: userMessage }]);
    this.prompt.set('');
    this.loading.set(true);

    this.http.post<{response: string}>('http://localhost:8000/chat', {
      user_id: 'test_user_angular',
      session_id: 'test_session_angular',
      message: userMessage
    }).subscribe({
      next: (res) => {
        this.messages.update(m => [...m, { role: 'assistant', content: res.response }]);
        this.loading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.messages.update(m => [...m, { role: 'assistant', content: `Error conectando al backend: ${err.message}` }]);
        this.loading.set(false);
      }
    });
  }
}
