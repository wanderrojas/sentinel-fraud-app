// shared.ts
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';
import { MessageService, ConfirmationService } from 'primeng/api';
import { NgxSpinnerModule } from 'ngx-spinner';
import { BadgeModule } from 'primeng/badge';
import { DatePickerModule } from 'primeng/datepicker';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { MenuModule } from 'primeng/menu';
import { SelectModule } from 'primeng/select';
import { MenubarModule } from 'primeng/menubar';
import { DataViewModule } from 'primeng/dataview';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TimelineModule } from 'primeng/timeline';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { AvatarModule } from 'primeng/avatar';
import { DrawerModule } from 'primeng/drawer';
import { TagModule } from 'primeng/tag';
import { DialogModule } from 'primeng/dialog';
import { PanelMenuModule } from 'primeng/panelmenu';
import { ChartModule } from 'primeng/chart';
import { OverlayBadgeModule } from 'primeng/overlaybadge';
import { DividerModule } from 'primeng/divider';
import { MessageModule } from 'primeng/message';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { AccordionModule } from 'primeng/accordion';
import { ProgressBarModule } from 'primeng/progressbar';
import { TooltipModule } from 'primeng/tooltip';
import { SkeletonModule } from 'primeng/skeleton';
import { FloatLabel } from 'primeng/floatlabel';
import { PasswordModule } from 'primeng/password';
import { HeaderTopComponent } from '@commons/components/layouts/header-top/header-top.component';

export const SHARED_IMPORTS = [
  HeaderTopComponent,

  FormsModule,
  ReactiveFormsModule,
  ButtonModule,
  CardModule,
  TableModule,
  ToastModule,
  NgxSpinnerModule,
  // RouterOutlet,

  //aaaaaaaaa
  InputNumberModule,
  // BrowserModule,

  // AppRoutingModule,
  MenubarModule,
  ButtonModule,
  DataViewModule,
  ProgressSpinnerModule,
  TimelineModule,
  ConfirmDialogModule,
  AvatarModule,
  DrawerModule,
  MenuModule,
  TagModule,
  DialogModule,
  FormsModule,
  SelectModule,
  CardModule,
  PanelMenuModule,
  ChartModule,
  DividerModule,

  BadgeModule,
  OverlayBadgeModule,
  ReactiveFormsModule,
  MessageModule,
  BreadcrumbModule,
  ProgressBarModule,

  TableModule,
  AccordionModule,
  TooltipModule,
  InputTextModule,
  ToastModule,
  SkeletonModule,
  FloatLabel,
  CardModule,
  DatePickerModule,
  PasswordModule,
  ButtonModule,
];

export const SHARED_PROVIDERS = [MessageService, ConfirmationService];
