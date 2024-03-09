from typing import List, TypedDict, Literal

from django.conf import settings
from django.db import models
from django.urls import reverse


class GptMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class RolePlayingRoom(models.Model):
    class Language(models.TextChoices):
        ENGLISH = "en-US", "English"
        JAPANESE = "ja-JP", "Japanese"
        CHINESE = "zh-CN", "Chinese"
        SPANISH = "es-ES", "Spanish"
        FRENCH = "fr-FR", "French"
        GERMAN = "de-DE", "German"
        RUSSIAN = "ru-RU", "Russian"

    class Level(models.IntegerChoices):
        BEGINNER = 1, "Beginner"
        INTERMEDIATE = 2, "Intermediate"
        ADVANCED = 3, "Advanced"

    class Meta:
        ordering = ["-pk"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.CharField(
        max_length=10,
        choices=Language.choices,
        default=Language.ENGLISH,
        verbose_name="Conversation Language",
    )
    level = models.SmallIntegerField(
        choices=Level.choices, default=Level.BEGINNER, verbose_name="Level"
    )
    situation = models.CharField(max_length=100, verbose_name="Situtation")
    situation_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Situation-EN",
        help_text="This field is utilized directly in the GPT prompt. If you leave it blank, the situation field will be translated and automatically reflected.",
    )
    my_role = models.CharField(max_length=100, verbose_name="My role")
    my_role_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="My role (EN)",
        help_text="This field is utilized directly in the GPT prompt. If you leave it blank, the my_role field will be translated and automatically reflected.",
    )
    gpt_role = models.CharField(max_length=100, verbose_name="GPT role")
    gpt_role_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="GPT role (EN)",
        help_text="This field is utilized directly in the GPT prompt. If you leave it blank, the gpt_role field will be translated and automatically reflected.",
    )

    def get_absolute_url(self) -> str:
        return reverse("role_playing_room_detail", args=[self.pk])

    def get_initial_messages(self) -> List[GptMessage]:
        gpt_name = "RolePlayingBot"
        language = self.get_language_display()
        situation_en = self.situation_en
        my_role_en = self.my_role_en
        gpt_role_en = self.gpt_role_en

        if self.level == self.Level.BEGINNER:
            level_string = f"a beginner in {language}"
            level_word = "simple"
        elif self.level == self.Level.INTERMEDIATE:
            level_string = f"a intermediate in {language}"
            level_word = "intermediate"
        elif self.level == self.Level.ADVANCED:
            level_string = f"a advanced learner in {language}"
            level_word = "advanced"
        else:
            raise ValueError(f"Invalid level : {self.level}")

        system_message = (
            f"You are helpful assistant supporting people learning {language}. "
            f"Your name is {gpt_name}. "
            f"Please assume that the user you are assisting is {level_string}. "
            f"And please write only the sentence without the character role."
        )

        user_message = (
            f"Let's have a conversation in {language}. "
            f"Please answer in {language} only "
            f"without providing a translation. "
            f"And please don't write down the pronunciation either. "
            f"Let us assume that the situation in '{situation_en}'. "
            f"I am {my_role_en}. The character I want you to act as is {gpt_role_en}. "
            f"Please make sure that I'm {level_string}, so please use {level_word} words "
            f"as much as possible. Now, start a conversation with the first sentence!"
        )

        return [
            GptMessage(role="system", content=system_message),
            GptMessage(role="user", content=user_message),
        ]

    def get_recommend_message(self) -> str:
        level = self.level

        if level == self.Level.BEGINNER:
            level_word = "simple"
        elif level == self.Level.INTERMEDIATE:
            level_word = "intermediate"
        elif level == self.Level.ADVANCED:
            level_word = "advanced"
        else:
            raise ValueError(f"Invalid level : {level}")

        return (
            f"Can you please provide me an {level_word} example "
            f"of how to respond to the last sentence "
            f"in this situation, without providing a translation "
            f"and any introductory phrases or sentences."
        )