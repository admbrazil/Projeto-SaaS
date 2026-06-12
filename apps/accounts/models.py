"""Modelo de usuário customizado — autenticação por CPF."""
import hashlib, hmac, uuid
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra):
        if not cpf:
            raise ValueError("CPF é obrigatório.")
        user = self.model(cpf=cpf, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(cpf, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        PATIENT     = "patient",     _("Paciente")
        DOCTOR      = "doctor",      _("Médico")
        HELPDESK    = "helpdesk",    _("Helpdesk")
        ADMIN       = "admin",       _("Administrador")
        SUPERADMIN  = "superadmin",  _("Super Admin")

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf           = models.CharField(max_length=11, unique=True, db_index=True)
    cpf_hash      = models.CharField(max_length=64, editable=False, db_index=True)
    email         = models.EmailField(blank=True)
    full_name     = models.CharField(max_length=255)
    role          = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    clinic        = models.ForeignKey("clinics.Clinic", on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="users")
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    date_joined   = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until  = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)
    lgpd_consent  = models.BooleanField(default=False)
    lgpd_consent_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD  = "cpf"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = _("Usuário")

    def __str__(self):
        return f"{self.full_name} ({self.cpf_masked})"

    def save(self, *args, **kwargs):
        self.cpf_hash = hmac.new(
            settings.SECRET_KEY.encode(), self.cpf.encode(), hashlib.sha256
        ).hexdigest()
        super().save(*args, **kwargs)

    @property
    def cpf_masked(self):
        c = self.cpf
        if len(c) == 11:
            return f"***.***.*{c[7:9]}-{c[9:]}"
        return "***.***.***-**"

    @property
    def is_locked(self):
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    def record_failed_login(self):
        from datetime import timedelta
        from django.conf import settings as s
        self.login_attempts += 1
        if self.login_attempts >= s.MAX_LOGIN_ATTEMPTS:
            self.locked_until = timezone.now() + timedelta(minutes=s.LOCKOUT_DURATION_MINUTES)
        self.save(update_fields=["login_attempts", "locked_until"])

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        self.save(update_fields=["login_attempts", "locked_until"])
