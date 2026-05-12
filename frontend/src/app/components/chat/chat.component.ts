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

import { MatCardModule }            from '@angular/material/card';
import { MatInputModule }           from '@angular/material/input';
import { MatButtonModule }          from '@angular/material/button';
import { MatIconModule }            from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule }           from '@angular/material/chips';
import { MatTooltipModule }         from '@angular/material/tooltip';

import { DiagnosisService, DiagnosisResponse } from '../../services/diagnosis.service';

export interface ChatMessage {
  type:      'user' | 'bot' | 'error';
  text:      string;
  timestamp: Date;
  diagnosis?: DiagnosisResponse;
  brand?:    string;
  model?:    string;
}

export interface CategoryMeta {
  key:   string;
  icon:  string;
  color: string;
  hint:  string;
}

export const CATEGORY_META: CategoryMeta[] = [
  { key: 'Energia',        icon: 'bolt',         color: '#f59e0b', hint: 'la PC no enciende o se apaga sola' },
  { key: 'Video',          icon: 'monitor',       color: '#0ea5e9', hint: 'no hay imagen o artefactos en pantalla' },
  { key: 'BIOS',           icon: 'memory',        color: '#a855f7', hint: 'la PC no pasa el POST o pitidos al encender' },
  { key: 'Almacenamiento', icon: 'storage',       color: '#10b981', hint: 'disco no detectado o errores SMART' },
  { key: 'Temperatura',    icon: 'thermostat',    color: '#ef4444', hint: 'CPU o GPU se sobrecalienta' },
  { key: 'Red',            icon: 'wifi_off',      color: '#06b6d4', hint: 'sin internet o adaptador de red falla' },
];

const CATEGORY_ICONS:  Record<string, string> = Object.fromEntries(CATEGORY_META.map(c => [c.key, c.icon]));
const CATEGORY_COLORS: Record<string, string> = Object.fromEntries(CATEGORY_META.map(c => [c.key, c.color]));

function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

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
  styleUrl:    './chat.component.scss',
})
export class ChatComponent {
  @ViewChild('chatContainer') private chatContainer!: ElementRef<HTMLDivElement>;

  private readonly diagnosisService = inject(DiagnosisService);

  readonly sessionId = generateSessionId();

  readonly messages = signal<ChatMessage[]>([
    {
      type:      'bot',
      text:      'Bienvenido al Asistente Técnico Inteligente. Describe el síntoma o falla de tu equipo. Puedes indicar la marca y modelo para un diagnóstico más preciso.',
      timestamp: new Date(),
    },
  ]);

  readonly userInput  = signal('');
  readonly brandInput = signal('');
  readonly modelInput = signal('');
  readonly isLoading  = signal(false);

  readonly canSend = computed(
    () => this.userInput().trim().length >= 3 && !this.isLoading()
  );

  readonly categoryMeta   = CATEGORY_META;
  readonly categoryIcons  = CATEGORY_ICONS;
  readonly categoryColors = CATEGORY_COLORS;

  sendMessage(): void {
    const text  = this.userInput().trim();
    const brand = this.brandInput().trim();
    const model = this.modelInput().trim();

    if (!this.canSend() || !text) return;

    this.messages.update(msgs => [
      ...msgs,
      { type: 'user', text, timestamp: new Date(), brand, model },
    ]);
    this.userInput.set('');
    this.isLoading.set(true);
    this.scrollToBottom();

    this.diagnosisService.diagnose({ mensaje: text, marca: brand, modelo: model }).subscribe({
      next: (result) => {
        this.messages.update(msgs => [
          ...msgs,
          { type: 'bot', text: result.solucion, timestamp: new Date(), diagnosis: result },
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

  quickDiagnose(hint: string): void {
    this.userInput.set(hint);
    setTimeout(() => {
      const textarea = document.querySelector<HTMLTextAreaElement>('.symptom-textarea');
      textarea?.focus();
    }, 50);
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

  getConfidenceClass(value: number): string {
    if (value >= 0.8) return 'confidence-high';
    if (value >= 0.5) return 'confidence-medium';
    return 'confidence-low';
  }

  getSeverityLabel(value: number): string {
    if (value >= 0.8) return 'Alta confianza';
    if (value >= 0.5) return 'Confianza media';
    return 'Baja confianza';
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const el = this.chatContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  }
}
