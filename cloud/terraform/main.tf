# Terraform Configuration for Real-Time Cloud-Based Event Planning & RSVP Tracker
# Infrastructure: AWS ECS Fargate, Application Load Balancer, RDS PostgreSQL, CloudWatch

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default     = "us-east-1"
  description = "AWS region for cloud deployment"
}

variable "environment" {
  default     = "production"
  description = "Environment name (production, staging)"
}

# ─── VPC & Networking ─────────────────────────────────────────────────────────
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "event-rsvp-vpc-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

# ─── Application Load Balancer (ALB) ──────────────────────────────────────────
resource "aws_lb" "alb" {
  name               = "event-rsvp-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

resource "aws_security_group" "alb_sg" {
  name        = "event-rsvp-alb-sg"
  description = "Allow inbound HTTP/HTTPS traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ─── Target Group with WebSocket sticky support ──────────────────────────────
resource "aws_lb_target_group" "backend_tg" {
  name        = "event-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }
}

# ─── ECS Fargate Cluster & Service ───────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "event-rsvp-cluster-${var.environment}"
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "event-rsvp-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "123456789012.dkr.ecr.${var.aws_region}.amazonaws.com/event-rsvp-backend:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "APP_NAME", value = "Cloud-Event-RSVP-Tracker" },
        { name = "ACCESS_TOKEN_EXPIRE_MINUTES", value = "1440" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/event-rsvp-backend"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])
}

# ─── Outputs ─────────────────────────────────────────────────────────────────
output "alb_dns_name" {
  value       = aws_lb.alb.dns_name
  description = "Public URL of Application Load Balancer"
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}
