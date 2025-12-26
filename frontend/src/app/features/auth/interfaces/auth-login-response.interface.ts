export interface AuthDTO {
  token: string;
  userData: UserData;
}

export interface UserData {
  usuario: string;
  nombreUsuario: string;
  rolId: number;
  rol: string;
  horaConeccion: string;
}
