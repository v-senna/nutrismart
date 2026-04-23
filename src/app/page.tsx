import { redirect } from 'next/navigation';

export default function Home() {
  // Redireciona a página inicial (raiz) diretamente para o login do nosso aplicativo NutriSmart
  redirect('/login');
}
