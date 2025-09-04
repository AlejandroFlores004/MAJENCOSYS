<?php
if(empty($_POST['name']) || empty($_POST['subject']) || empty($_POST['message']) || !filter_var($_POST['email'], FILTER_VALIDATE_EMAIL)) {
  http_response_code(500);
  exit();
}

$name = strip_tags(htmlspecialchars($_POST['name']));
$email = strip_tags(htmlspecialchars($_POST['email']));
$m_subject = strip_tags(htmlspecialchars($_POST['subject']));
$message = strip_tags(htmlspecialchars($_POST['message']));

$to = "ianponcemontano@gmail.com"; // Cambie este correo electrónico al suyo. //
$subject = "$m_subject:  $name";
$body = "Has recibido un nuevo mensaje del formulario de contacto de tu sitio web.\n\n"."Aquí están los detalles:\n\nNombre: $name\n\n\nEmail: $email\n\nMotivo: $m_subject\n\nMensaje: $message";
$header = "De: $email";
$header .= "Responder a: $email";	

if(!mail($to, $subject, $body, $header))
  http_response_code(500);
?>
