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

import {
  DiagnosisService,
  DiagnosisResponse,
  DiagnosisResult,
  ClarificationResult,
} from '../../services/diagnosis.service';

// -----------------------------------------------------------------------
// Catálogo de marcas y series
// -----------------------------------------------------------------------
export interface BrandSeries { name: string; type: string; }
export interface BrandInfo   { name: string; color: string; series: BrandSeries[]; }

const BRANDS_DATA: BrandInfo[] = [
  {
    name: 'Dell', color: '#007DB8',
    series: [
      { name: 'XPS',       type: 'laptop'      },
      { name: 'Inspiron',  type: 'laptop'      },
      { name: 'Latitude',  type: 'laptop'      },
      { name: 'Alienware', type: 'gaming'      },
      { name: 'OptiPlex',  type: 'desktop'     },
      { name: 'Precision', type: 'workstation' },
    ],
  },
  {
    name: 'HP', color: '#0096D6',
    series: [
      { name: 'Pavilion',  type: 'laptop'      },
      { name: 'Spectre',   type: 'laptop'      },
      { name: 'EliteBook', type: 'laptop'      },
      { name: 'ProBook',   type: 'laptop'      },
      { name: 'Omen',      type: 'gaming'      },
      { name: 'Envy',      type: 'laptop'      },
      { name: 'ZBook',     type: 'workstation' },
    ],
  },
  {
    name: 'Lenovo', color: '#E2231A',
    series: [
      { name: 'ThinkPad',    type: 'laptop'   },
      { name: 'IdeaPad',     type: 'laptop'   },
      { name: 'Legion',      type: 'gaming'   },
      { name: 'Yoga',        type: 'laptop'   },
      { name: 'ThinkCentre', type: 'desktop'  },
      { name: 'IdeaCentre',  type: 'desktop'  },
    ],
  },
  {
    name: 'ASUS', color: '#00539B',
    series: [
      { name: 'VivoBook',   type: 'laptop'      },
      { name: 'ZenBook',    type: 'laptop'      },
      { name: 'ROG',        type: 'gaming'      },
      { name: 'TUF',        type: 'gaming'      },
      { name: 'ExpertBook', type: 'laptop'      },
      { name: 'ProArt',     type: 'workstation' },
    ],
  },
  {
    name: 'Acer', color: '#83B81A',
    series: [
      { name: 'Aspire',     type: 'laptop'  },
      { name: 'Swift',      type: 'laptop'  },
      { name: 'Nitro',      type: 'gaming'  },
      { name: 'Predator',   type: 'gaming'  },
      { name: 'TravelMate', type: 'laptop'  },
    ],
  },
  {
    name: 'MSI', color: '#E5002B',
    series: [
      { name: 'GF Series',  type: 'gaming'      },
      { name: 'GE Series',  type: 'gaming'      },
      { name: 'Stealth',    type: 'gaming'      },
      { name: 'Creator',    type: 'workstation' },
      { name: 'Prestige',   type: 'laptop'      },
    ],
  },
  {
    name: 'Generica', color: '#607D8B',
    series: [
      { name: 'PC Escritorio', type: 'desktop' },
      { name: 'Laptop',        type: 'laptop'  },
      { name: 'Gaming PC',     type: 'gaming'  },
    ],
  },
];

// -----------------------------------------------------------------------
// Interfaces de mensajes
// -----------------------------------------------------------------------
export interface ChatMessage {
  type: 'user' | 'bot' | 'error';
  text: string;
  timestamp: Date;
  diagnosis?:     DiagnosisResult;
  clarification?: ClarificationResult;
  logId?:         string | null;
  feedbackSent?:  'positive' | 'negative' | null;
  /** Marca/serie con que se realizó el diagnóstico */
  marca?: string | null;
  serie?: string | null;
}

// -----------------------------------------------------------------------
// Mapas de íconos y colores de categoría
// -----------------------------------------------------------------------
const CATEGORY_ICONS: Record<string, string> = {
  Energia:        'power',
  Video:          'monitor',
  BIOS:           'memory',
  Almacenamiento: 'storage',
  Red:            'wifi',
  Audio:          'volume_up',
  Temperatura:    'thermostat',
  USB:            'usb',
  Drivers:        'settings',
};

const CATEGORY_COLORS: Record<string, string> = {
  Energia:        '#e53935',
  Video:          '#1e88e5',
  BIOS:           '#8e24aa',
  Almacenamiento: '#43a047',
  Red:            '#00897b',
  Audio:          '#f4511e',
  Temperatura:    '#fb8c00',
  USB:            '#6d4c41',
  Drivers:        '#546e7a',
};

// -----------------------------------------------------------------------
// Componente
// -----------------------------------------------------------------------
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

  // ── Catálogo de marcas expuesto al template
  readonly brands = BRANDS_DATA;

  // ── Mensajes del chat
  readonly messages = signal<ChatMessage[]>([
    {
      type: 'bot',
      text: '¡Hola! Soy tu asistente de diagnóstico de hardware. Selecciona tu marca y serie (opcional) y luego describe el síntoma o falla de tu equipo.',
      timestamp: new Date(),
    },
  ]);

  readonly userInput  = signal('');
  readonly isLoading  = signal(false);

  // ── Selección de marca/serie
  readonly selectedBrand  = signal<string | null>(null);
  readonly selectedSeries = signal<string | null>(null);

  readonly availableSeries = computed<BrandSeries[]>(() => {
    const b = this.selectedBrand();
    return b ? (BRANDS_DATA.find(br => br.name === b)?.series ?? []) : [];
  });

  readonly selectedBrandColor = computed<string>(() => {
    const b = this.selectedBrand();
    return b ? (BRANDS_DATA.find(br => br.name === b)?.color ?? '#546e7a') : '#546e7a';
  });

  // ── Contexto multi-turno
  private readonly pendingContext = signal<string[]>([]);

  readonly canSend = computed(
    () => this.userInput().trim().length >= 3 && !this.isLoading()
  );

  readonly categoryIcons  = CATEGORY_ICONS;
  readonly categoryColors = CATEGORY_COLORS;

  // ── Selección de marca
  selectBrand(name: string): void {
    if (this.selectedBrand() === name) {
      this.selectedBrand.set(null);
      this.selectedSeries.set(null);
    } else {
      this.selectedBrand.set(name);
      this.selectedSeries.set(null);
    }
  }

  selectSeries(name: string): void {
    this.selectedSeries.set(this.selectedSeries() === name ? null : name);
  }

  clearBrandSelection(): void {
    this.selectedBrand.set(null);
    this.selectedSeries.set(null);
  }

  // ── Envío de mensaje
  sendMessage(): void {
    const text = this.userInput().trim();
    if (!this.canSend() || !text) return;

    const marca  = this.selectedBrand()  ?? undefined;
    const serie  = this.selectedSeries() ?? undefined;
    const context = this.pendingContext();

    this.messages.update(msgs => [
      ...msgs,
      { type: 'user', text, timestamp: new Date() },
    ]);
    this.userInput.set('');
    this.isLoading.set(true);
    this.scrollToBottom();

    this.diagnosisService.diagnose(text, context, marca, serie).subscribe({
      next: (result: DiagnosisResponse) => {
        if (result.necesita_mas_info) {
          this.pendingContext.update(ctx => [...ctx, text]);
          this.messages.update(msgs => [
            ...msgs,
            {
              type: 'bot',
              text: result.pregunta,
              timestamp: new Date(),
              clarification: result as ClarificationResult,
            },
          ]);
        } else {
          this.pendingContext.set([]);
          const diag = result as DiagnosisResult;
          this.messages.update(msgs => [
            ...msgs,
            {
              type: 'bot',
              text:         diag.solucion,
              timestamp:    new Date(),
              diagnosis:    diag,
              logId:        diag.log_id,
              feedbackSent: null,
              marca:        diag.marca,
              serie:        diag.serie,
            },
          ]);
        }
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

  // ── Feedback
  sendFeedback(msgIndex: number, util: boolean): void {
    const msg = this.messages()[msgIndex];
    if (!msg?.logId || msg.feedbackSent != null) return;

    this.messages.update(list =>
      list.map((m, i) =>
        i === msgIndex
          ? { ...m, feedbackSent: util ? 'positive' : 'negative' }
          : m
      )
    );

    this.diagnosisService.sendFeedback(msg.logId, util).subscribe({
      error: () => {
        this.messages.update(list =>
          list.map((m, i) =>
            i === msgIndex ? { ...m, feedbackSent: null } : m
          )
        );
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
    setTimeout(() => {
      const el = this.chatContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  }
}
