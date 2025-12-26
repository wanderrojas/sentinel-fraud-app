import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { SpinnerService } from '../../../../commons/services/spinner.service';
import { HelperService } from '../../../../commons/services/helper.service';
import { AuthService } from '../../services/auth.service';
import { MessageType } from '../../../../commons/constants/MessageType';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [...SHARED_IMPORTS],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  messageService = inject(MessageService);
  spinnerService = inject(SpinnerService);

  loginForm: FormGroup;

  helperService = inject(HelperService);
  router = inject(Router);
  authService = inject(AuthService);

  constructor(private fb: FormBuilder) {
    this.loginForm = this.buildForm();
  }

  private buildForm(): FormGroup {
    return this.fb.group({
      username: ['admin@gmail.com', [Validators.required, Validators.email]],
      password: ['admin123', [Validators.required, Validators.minLength(6)]],
    });
  }

  onSubmit(): void {
    this.spinnerService.showFullScreen(
      'Validando sus credenciales, espere por favor...'
    );

    if (!this.loginForm.valid) {
      this.messageService.add(
        this.helperService.buildMessagePrime(
          MessageType.ERROR,
          'Por favor completa todos los campos correctamente'
        )
      );

      this.loginForm.markAllAsTouched();
      this.spinnerService.hideFullScreen();
      return;
    }

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        setTimeout(() => {
          this.spinnerService.hideFullScreen();

          this.helperService.showMessage(
            MessageType.SUCCESS,
            'Validación de credenciales realizada correctamente'
          );
          this.router.navigate(['/dashboard']);
        }, 1000);
      },
      error: (err) => this.spinnerService.hideFullScreen(),
    });
  }
}
