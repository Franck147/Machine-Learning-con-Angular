import {
  Component,
  ElementRef,
  ViewChild,
  inject,
  signal,
  computed,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

// Angular Material
import { MatCardModule }            from '@angular/material/card';
import { MatInputModule }           from '@angular/material/input';
import { MatButtonModule }          from '@angular/material/button';
import { MatIconModule }            from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule }           from '@angular/material/chips';
import { MatTooltipModule }         from '@angular/material/tooltip';

import { DiagnosisService, DiagnosisResponse } from '../../services/diagnosis.service';

export interface ChatMessage {
  type: 'user' | 'bot' | 'error';
  text: string;
  timestamp: Date;
  diagnosis?: DiagnosisResponse;
}

const CATEGORY_ICONS: Record<string, string> = {
  Energia:        'power',
  Video:          'monitor',
  BIOS:           'memory',
  Almacenamiento: 'storage',
};

const CATEGORY_COLORS: Record<string, string> = {
  Energia:        '#e53935',
  Video:          '#1e88e5',
  BIOS:           '#8e24aa',
  Almacenamiento: '#43a047',
};

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTooltipModule,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent {
  @ViewChild('chatContainer') private chatContainer!: ElementRef<HTMLDivElement>;

  private readonly diagnosisService = inject(DiagnosisService);

  readonly messages = signal<ChatMessage[]>([
    {
      type: 'bot',
      text: '¡Hola! Soy tu asistente de diagnóstico de hardware. Describe el síntoma o falla que presenta tu equipo y te ayudaré a identificar el problema.',
      timestamp: new Date(),
    },
  ]);

  readonly userInput = signal('');
  readonly isLoading = signal(false);

  readonly canSend = computed(
    () => this.userInput().trim().length >= 3 && !this.isLoading()
  );

  readonly categoryIcons  = CATEGORY_ICONS;
  readonly categoryColors = CATEGORY_COLORS;

  sendMessage(): void {
    const text = this.userInput().trim();
    if (!this.canSend() || !text) return;

    this.messages.update(msgs => [
      ...msgs,
      { type: 'user', text, timestamp: new Date() },
    ]);
    this.userInput.set('');
    this.isLoading.set(true);
    this.scrollToBottom();

    this.diagnosisService.diagnose(text).subscribe({
      next: (result) => {
        this.messages.update(msgs => [
          ...msgs,
          {
            type: 'bot',
            text: result.solucion,
            timestamp: new Date(),
            diagnosis: result,
          },
        ]);
        this.isLoading.set(false);
        this.scrollToBottom();
      },
      error: (err: Error) => {
        this.messages.update(msgs => [
          ...msgs,
          { type: 'error', text: err.message, timestamp: new Date() },
        ]);
        this.isLoading.set(false);
        this.scrollToBottom();
      },
    });
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  confidencePercent(value: number): string {
    return `${(value * 100).toFixed(0)}%`;
  }

  private scrollToBottom(): void {
    // Espera al siguiente tick para que el DOM se actualice
    setTimeout(() => {
      const el = this.chatContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  }
}
