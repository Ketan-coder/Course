from django.db import models

class Tier(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_score = models.PositiveIntegerField(default=0)
    icon = models.ImageField(upload_to='tier_icons', blank=True, null=True)  # Added icon
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['min_score']

class TierRank(models.Model):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='ranks')
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='tier_ranks', blank=True, null=True)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)  # Added order field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return f"{self.tier.name} - {self.name}"  

    class Meta:
        unique_together = ['tier', 'name']
        ordering = ['tier__min_score', 'order'] 

class Tournament(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField('Users.Profile', related_name='joined_tournaments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_date', 'name']
        verbose_name_plural = 'Tournaments' 

class LeaderboardEntry(models.Model):
    profile = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='leaderboard_profile')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='leaderboard_entries')
    score = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'tournament')
        ordering = ['-score', 'timestamp']

    def __str__(self):
        return f"{self.profile.user.username} - {self.tournament.name} - {self.score}"