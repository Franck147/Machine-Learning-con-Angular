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

// ─── Marcas y series ──────────────────────────────────────────────────────────
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
      { name: 'Vostro',    type: 'laptop'      },
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
      { name: 'ThinkPad',    type: 'laptop'      },
      { name: 'IdeaPad',     type: 'laptop'      },
      { name: 'Legion',      type: 'gaming'      },
      { name: 'Yoga',        type: 'laptop'      },
      { name: 'ThinkCentre', type: 'desktop'     },
      { name: 'IdeaCentre',  type: 'desktop'     },
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
    name: 'Apple', color: '#A2AAAD',
    series: [
      { name: 'MacBook Air', type: 'laptop'      },
      { name: 'MacBook Pro', type: 'laptop'      },
      { name: 'Mac mini',    type: 'desktop'     },
      { name: 'Mac Studio',  type: 'workstation' },
      { name: 'iMac',        type: 'desktop'     },
      { name: 'iPad',        type: 'laptop'      },
    ],
  },
  {
    name: 'Samsung', color: '#1428A0',
    series: [
      { name: 'Galaxy Book', type: 'laptop' },
      { name: 'Galaxy Tab',  type: 'laptop' },
    ],
  },
  {
    name: 'Huawei', color: '#CF0A2C',
    series: [
      { name: 'MateBook', type: 'laptop' },
      { name: 'MatePad',  type: 'laptop' },
    ],
  },
  {
    name: 'Toshiba', color: '#EA0E0E',
    series: [
      { name: 'Satellite', type: 'laptop' },
      { name: 'Dynabook',  type: 'laptop' },
    ],
  },
  {
    name: 'Microsoft', color: '#737373',
    series: [
      { name: 'Surface Pro',    type: 'laptop' },
      { name: 'Surface Laptop', type: 'laptop' },
      { name: 'Surface Book',   type: 'laptop' },
    ],
  },
  {
    name: 'Xiaomi', color: '#FF6900',
    series: [
      { name: 'Mi Notebook', type: 'laptop' },
      { name: 'Pad',         type: 'laptop' },
    ],
  },
  {
    name: 'Amazon', color: '#FF9900',
    series: [
      { name: 'Fire',    type: 'laptop' },
      { name: 'Fire HD', type: 'laptop' },
    ],
  },
  {
    name: 'Gigabyte', color: '#E6242A',
    series: [
      { name: 'AORUS',    type: 'gaming'  },
      { name: 'B Series', type: 'desktop' },
      { name: 'Z Series', type: 'desktop' },
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

// ─── Íconos por tipo de serie ─────────────────────────────────────────────────
const TYPE_ICONS: Record<string, string> = {
  laptop:      'laptop',
  gaming:      'sports_esports',
  desktop:     'desktop_windows',
  workstation: 'engineering',
};

// ─── Categorías ───────────────────────────────────────────────────────────────
const CATEGORY_ICONS: Record<string, string> = {
  Energia:          'bolt',
  Video:            'monitor',
  BIOS:             'memory',
  Almacenamiento:   'storage',
  Red:              'wifi',
  Audio:            'volume_up',
  Temperatura:      'thermostat',
  USB:              'usb',
  Drivers:          'settings',
  Corto:            'warning',
  SistemaOperativo: 'bug_report',
};

const CATEGORY_COLORS: Record<string, string> = {
  Energia:          '#ef5350',
  Video:            '#42a5f5',
  BIOS:             '#ab47bc',
  Almacenamiento:   '#66bb6a',
  Red:              '#26a69a',
  Audio:            '#ff7043',
  Temperatura:      '#ffa726',
  USB:              '#8d6e63',
  Drivers:          '#78909c',
  Corto:            '#ff1744',
  SistemaOperativo: '#1565c0',
};

// ─── Estado del comentario por mensaje ────────────────────────────────────────
export interface CommentState {
  /** Caja de comentario visible */
  open:        boolean;
  /** Texto del comentario libre */
  text:        string;
  /** Categoría seleccionada como corrección (null = no se corrige) */
  cat:         string | null;
  /** true cuando ya se envió o se omitió */
  done:        boolean;
}

// ─── Mensaje ──────────────────────────────────────────────────────────────────
export interface ChatMessage {
  type: 'user' | 'bot' | 'error';
  text: string;
  timestamp: Date;
  diagnosis?:     DiagnosisResult;
  clarification?: ClarificationResult;
  logId?:         string | null;
  feedbackSent?:  'positive' | 'negative' | null;
  marca?:         string | null;
  serie?:         string | null;
}

// ─── Componente ───────────────────────────────────────────────────────────────
@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatCardModule, MatInputModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, MatChipsModule, MatTooltipModule,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent {
  @ViewChild('chatContainer') private chatContainer!: ElementRef<HTMLDivElement>;

  private readonly diagnosisService = inject(DiagnosisService);

  readonly brands      = BRANDS_DATA;
  readonly typeIcons   = TYPE_ICONS;
  readonly categoryIcons  = CATEGORY_ICONS;
  readonly categoryColors = CATEGORY_COLORS;

  // Stats del sistema
  readonly systemStats = {
    ejemplos:   2910,
    categorias: 11,
    marcas:     15,
    algoritmo:  'LinearSVC',
  };

  readonly messages = signal<ChatMessage[]>([
    {
      type: 'bot',
      text: '¡Bienvenido al asistente de diagnóstico de hardware! Selecciona tu marca y serie para obtener soluciones específicas, luego describe el problema de tu equipo.',
      timestamp: new Date(),
    },
  ]);

  readonly userInput  = signal('');
  readonly isLoading  = signal(false);

  readonly selectedBrand  = signal<string | null>(null);
  readonly selectedSeries = signal<string | null>(null);

  private readonly pendingContext = signal<string[]>([]);

  readonly availableSeries = computed<BrandSeries[]>(() => {
    const b = this.selectedBrand();
    return b ? (BRANDS_DATA.find(br => br.name === b)?.series ?? []) : [];
  });

  readonly selectedBrandColor = computed<string>(() => {
    const b = this.selectedBrand();
    return b ? (BRANDS_DATA.find(br => br.name === b)?.color ?? '#ef5350') : '#ef5350';
  });

  readonly canSend = computed(
    () => this.userInput().trim().length >= 3 && !this.isLoading()
  );

  /** Mapa de estados de comentario, indexado por posición del mensaje */
  readonly commentStates = signal<Map<number, CommentState>>(new Map());

  /** Lista de categorías para el selector de corrección */
  readonly allCategories = Object.keys(CATEGORY_ICONS);

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

  sendMessage(): void {
    const text  = this.userInput().trim();
    if (!this.canSend() || !text) return;

    const marca   = this.selectedBrand()  ?? undefined;
    const serie   = this.selectedSeries() ?? undefined;
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
              text: diag.solucion,
              timestamp: new Date(),
              diagnosis: diag,
              logId: diag.log_id,
              feedbackSent: null,
              marca: diag.marca,
              serie: diag.serie,
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

  // ── Feedback + comentario ─────────────────────────────────────────────────

  /** Paso 1: clic en 👍 / 👎 — marca selección y abre la caja de comentario */
  selectFeedback(msgIndex: number, util: boolean): void {
    const msg = this.messages()[msgIndex];
    if (!msg?.logId || msg.feedbackSent != null) return;

    // Marcar selección en UI (optimistic)
    this.messages.update(list =>
      list.map((m, i) =>
        i === msgIndex ? { ...m, feedbackSent: util ? 'positive' : 'negative' } : m
      )
    );

    // Abrir caja de comentario
    this.commentStates.update(map => {
      const next = new Map(map);
      next.set(msgIndex, { open: true, text: '', cat: null, done: false });
      return next;
    });
  }

  /** Actualiza el texto del comentario mientras el usuario escribe */
  setCommentText(msgIndex: number, text: string): void {
    this.commentStates.update(map => {
      const next = new Map(map);
      const cur  = next.get(msgIndex);
      if (cur) next.set(msgIndex, { ...cur, text });
      return next;
    });
  }

  /** Selecciona/deselecciona una categoría de corrección */
  toggleCommentCat(msgIndex: number, cat: string): void {
    this.commentStates.update(map => {
      const next = new Map(map);
      const cur  = next.get(msgIndex);
      if (cur) next.set(msgIndex, { ...cur, cat: cur.cat === cat ? null : cat });
      return next;
    });
  }

  /** Paso 2: envía feedback + comentario + corrección de categoría */
  submitComment(msgIndex: number): void {
    const msg   = this.messages()[msgIndex];
    const state = this.commentStates().get(msgIndex);
    if (!msg?.logId || !state) return;

    const util    = msg.feedbackSent === 'positive';
    const comment = state.text.trim() || undefined;
    const catCorr = state.cat || undefined;

    this.diagnosisService.sendFeedback(msg.logId, util, comment, catCorr).subscribe({
      next: () => {
        this.commentStates.update(map => {
          const next = new Map(map);
          next.set(msgIndex, { ...state, done: true });
          return next;
        });
      },
      error: () => {
        // Si falla, cerrar igual para no bloquear al usuario
        this.commentStates.update(map => {
          const next = new Map(map);
          next.set(msgIndex, { ...state, done: true });
          return next;
        });
      },
    });
  }

  /** Omitir comentario: envía solo el feedback sin texto adicional */
  skipComment(msgIndex: number): void {
    const msg   = this.messages()[msgIndex];
    const state = this.commentStates().get(msgIndex);
    if (!msg?.logId || !state) return;

    const util = msg.feedbackSent === 'positive';
    this.diagnosisService.sendFeedback(msg.logId, util).subscribe();

    this.commentStates.update(map => {
      const next = new Map(map);
      next.set(msgIndex, { ...state, done: true });
      return next;
    });
  }

  getCommentState(msgIndex: number): CommentState | undefined {
    return this.commentStates().get(msgIndex);
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

  confidenceWidth(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }

  confidenceClass(value: number): string {
    if (value >= 0.8) return 'high';
    if (value >= 0.6) return 'medium';
    return 'low';
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const el = this.chatContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    }, 50);
  }
}
