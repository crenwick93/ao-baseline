output "instance_public_ip" {
  description = "Elastic IP of the demo EC2 instance (stable across stop/start)"
  value       = aws_eip.demo.public_ip
}

output "ssh_command" {
  description = "SSH into the instance"
  value       = "ssh -i ${abspath(local_sensitive_file.ssh_private_key.filename)} ec2-user@${aws_eip.demo.public_ip}"
}

output "http_url" {
  description = "HTTP endpoint of the demo host"
  value       = "http://${aws_eip.demo.public_ip}"
}
