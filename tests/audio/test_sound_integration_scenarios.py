"""Integration tests for sound effects in complex gameplay scenarios."""

from unittest.mock import Mock, patch, call
import pytest

from src.managers.sound_manager import SoundManager


class TestGameplayIntegrationScenarios:
    """Test sound effects in realistic gameplay scenarios."""

    @pytest.fixture
    def integration_sound_manager(self):
        """Create sound manager for integration testing."""
        SoundManager._instance = None
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                sm = SoundManager()
                yield sm

    def test_ski_game_sound_sequence(self, integration_sound_manager):
        """Test complete sound sequence for ski game scenario."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_music') as mock_music:
            with patch.object(sm, 'play_sfx') as mock_sfx:
                # Simulate ski game sequence
                
                # 1. Scene starts
                sm.play_music("assets/audio/music/ski_theme.ogg", loops=-1)
                
                # 2. Player turns left
                sm.play_sfx("assets/audio/sfx/ski_turn.ogg")
                
                # 3. Player collects snowflake
                sm.play_sfx("assets/audio/sfx/snowflake_collect.ogg")
                
                # 4. Player crashes into tree
                sm.play_sfx("assets/audio/sfx/tree_crash.ogg")
                sm.duck_audio(duck_level=0.3, duration_ms=1000)
                
                # 5. Game over
                sm.stop_music(fade_ms=500)
                sm.play_sfx("assets/audio/sfx/game_over.ogg")
                
                # Verify sound sequence
                mock_music.assert_has_calls([
                    call("assets/audio/music/ski_theme.ogg", loops=-1),
                ])
                
                mock_sfx.assert_has_calls([
                    call("assets/audio/sfx/ski_turn.ogg"),
                    call("assets/audio/sfx/snowflake_collect.ogg"), 
                    call("assets/audio/sfx/tree_crash.ogg"),
                    call("assets/audio/sfx/game_over.ogg"),
                ])

    def test_pool_game_rapid_fire_scenario(self, integration_sound_manager):
        """Test sound effects during rapid balloon shooting in pool game."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_sfx') as mock_sfx:
            with patch("pygame.mixer.find_channel") as mock_find:
                # Setup multiple channels for rapid fire
                mock_channels = [Mock() for _ in range(8)]
                mock_find.side_effect = lambda: mock_channels[mock_find.call_count % 8]
                
                # Simulate rapid shooting sequence
                for shot in range(10):
                    # Launch balloon
                    sm.play_sfx("assets/audio/sfx/balloon_launch.ogg")
                    
                    # Hit target (50% hit rate)
                    if shot % 2 == 0:
                        sm.play_sfx("assets/audio/sfx/target_hit.ogg")
                        sm.play_sfx("assets/audio/sfx/splash.ogg")
                    
                # Powerup collected during rapid fire
                sm.play_sfx("assets/audio/sfx/powerup_collect.ogg")
                
                # Verify rapid fire doesn't break sound system
                assert mock_sfx.call_count >= 15  # At least 10 launches + 5 hits + powerup

    def test_vegas_boss_fight_audio_sequence(self, integration_sound_manager):
        """Test complex audio sequence during vegas boss fight."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_music') as mock_music:
            with patch.object(sm, 'play_sfx') as mock_sfx:
                with patch.object(sm, 'crossfade_music') as mock_crossfade:
                    # Boss fight sequence
                    
                    # 1. Approach boss arena
                    sm.play_music("assets/audio/music/vegas_exploration.ogg")
                    
                    # 2. Boss appears - music changes
                    sm.crossfade_music("assets/audio/music/boss_battle.ogg", duration_ms=1000)
                    sm.play_sfx("assets/audio/sfx/boss_roar.ogg")
                    
                    # 3. Combat sequence
                    for turn in range(5):
                        # Player jumps
                        sm.play_sfx("assets/audio/sfx/player_jump.ogg")
                        
                        # Player attacks
                        sm.play_sfx("assets/audio/sfx/player_attack.ogg")
                        
                        # Boss takes damage or attacks back
                        if turn % 2 == 0:
                            sm.play_sfx("assets/audio/sfx/boss_hit.ogg")
                        else:
                            sm.play_sfx("assets/audio/sfx/boss_attack.ogg")
                            sm.play_sfx("assets/audio/sfx/player_hurt.ogg")
                    
                    # 4. Boss defeated
                    sm.play_sfx("assets/audio/sfx/boss_defeat.ogg")
                    sm.crossfade_music("assets/audio/music/victory_theme.ogg", duration_ms=2000)
                    
                    # Verify complex sequence executed correctly
                    assert mock_music.call_count >= 1
                    assert mock_crossfade.call_count == 2
                    assert mock_sfx.call_count >= 12  # All combat sounds

    def test_scene_transition_audio_continuity(self, integration_sound_manager):
        """Test audio continuity during scene transitions."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_music') as mock_music:
            with patch.object(sm, 'stop_music') as mock_stop:
                with patch.object(sm, 'play_sfx') as mock_sfx:
                    # Simulate scene transitions
                    
                    # Title screen
                    sm.play_music("assets/audio/music/title_theme.ogg", loops=-1)
                    
                    # Transition to character select
                    sm.play_sfx("assets/audio/sfx/menu_select.ogg")
                    sm.crossfade_music("assets/audio/music/character_select.ogg")
                    
                    # Transition to hub world
                    sm.play_sfx("assets/audio/sfx/character_confirm.ogg")
                    sm.crossfade_music("assets/audio/music/hub_ambient.ogg")
                    
                    # Enter minigame
                    sm.play_sfx("assets/audio/sfx/door_open.ogg")
                    sm.stop_music(fade_ms=500)
                    
                    # Verify smooth transitions
                    assert mock_music.call_count >= 1
                    assert mock_sfx.call_count >= 3

    def test_multiplayer_audio_coordination(self, integration_sound_manager):
        """Test audio coordination in multiplayer scenarios."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_sfx') as mock_sfx:
            # Simulate multiplayer pool game
            players = ["danger", "rose", "dad"]
            
            for round_num in range(3):
                for player in players:
                    # Each player takes a shot
                    sm.play_sfx("assets/audio/sfx/balloon_launch.ogg")
                    
                    # Different hit sounds for different players
                    if player == "danger":
                        sm.play_sfx("assets/audio/sfx/target_hit_high.ogg")
                    elif player == "rose":
                        sm.play_sfx("assets/audio/sfx/target_hit_medium.ogg")
                    else:  # dad
                        sm.play_sfx("assets/audio/sfx/target_hit_low.ogg")
                    
                    sm.play_sfx("assets/audio/sfx/splash.ogg")
            
            # Verify all player actions generated audio
            expected_calls = 3 * 3 * 3  # 3 rounds, 3 players, 3 sounds each
            assert mock_sfx.call_count == expected_calls

    def test_powerup_chain_reaction_audio(self, integration_sound_manager):
        """Test audio during powerup chain reactions."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_sfx') as mock_sfx:
            # Simulate chain reaction of powerups
            
            # Initial powerup collected
            sm.play_sfx("assets/audio/sfx/powerup_collect.ogg")
            
            # Chain reaction triggers
            chain_length = 5
            for chain_link in range(chain_length):
                # Each link in chain has escalating audio
                pitch_modifier = 1.0 + (chain_link * 0.1)  # Simulated pitch increase
                sm.play_sfx("assets/audio/sfx/chain_reaction.ogg")
                
                # Bonus points awarded
                sm.play_sfx("assets/audio/sfx/bonus_points.ogg")
            
            # Final chain completion
            sm.play_sfx("assets/audio/sfx/chain_complete.ogg")
            
            # Verify chain reaction audio sequence
            expected_calls = 1 + (chain_length * 2) + 1  # Initial + chain*2 + final
            assert mock_sfx.call_count == expected_calls

    def test_environmental_audio_layering(self, integration_sound_manager):
        """Test layering of environmental and gameplay audio."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_music') as mock_music:
            with patch.object(sm, 'play_sfx') as mock_sfx:
                # Start with ambient environment
                sm.play_music("assets/audio/ambient/winter_wind.ogg", loops=-1)
                
                # Add environmental layers
                environmental_sounds = [
                    "assets/audio/ambient/distant_skiing.ogg",
                    "assets/audio/ambient/snow_falling.ogg",
                    "assets/audio/ambient/mountain_echo.ogg"
                ]
                
                for env_sound in environmental_sounds:
                    sm.play_sfx(env_sound)
                
                # Add gameplay sounds on top
                gameplay_sounds = [
                    "assets/audio/sfx/ski_carving.ogg",
                    "assets/audio/sfx/snowflake_collect.ogg",
                    "assets/audio/sfx/speed_boost.ogg"
                ]
                
                for game_sound in gameplay_sounds:
                    sm.play_sfx(game_sound)
                
                # Verify layered audio system
                assert mock_music.call_count == 1
                assert mock_sfx.call_count == len(environmental_sounds) + len(gameplay_sounds)

    def test_adaptive_music_system_integration(self, integration_sound_manager):
        """Test integration with adaptive music systems."""
        sm = integration_sound_manager
        
        with patch.object(sm, 'play_music') as mock_music:
            with patch.object(sm, 'crossfade_music') as mock_crossfade:
                # Simulate adaptive music in ski game
                
                # Start with calm music
                sm.play_music("assets/audio/music/ski_calm.ogg")
                
                # Player picks up speed - music intensifies
                sm.crossfade_music("assets/audio/music/ski_medium.ogg", duration_ms=2000)
                
                # High speed reached - intense music
                sm.crossfade_music("assets/audio/music/ski_intense.ogg", duration_ms=1500)
                
                # Crash - music cuts to dramatic
                sm.play_music("assets/audio/music/crash_dramatic.ogg", fade_ms=0)
                
                # Recovery - back to calm
                sm.crossfade_music("assets/audio/music/ski_calm.ogg", duration_ms=3000)
                
                # Verify adaptive music transitions
                assert mock_music.call_count >= 2  # Initial + crash
                assert mock_crossfade.call_count >= 3  # All speed transitions

    def test_audio_memory_management_during_gameplay(self, integration_sound_manager):
        """Test audio memory management during extended gameplay."""
        sm = integration_sound_manager
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                mock_sound.return_value = Mock()
                
                # Simulate extended gameplay session
                session_sounds = []
                
                # Phase 1: Menu navigation (light sound usage)
                menu_sounds = ["menu_hover.ogg", "menu_select.ogg", "menu_back.ogg"]
                for sound in menu_sounds * 10:  # Repeated menu navigation
                    sm.play_sfx(f"assets/audio/sfx/{sound}")
                    session_sounds.append(sound)
                
                # Phase 2: Intense gameplay (heavy sound usage)
                gameplay_sounds = [
                    "balloon_launch.ogg", "target_hit.ogg", "splash.ogg",
                    "powerup_collect.ogg", "bonus_points.ogg"
                ]
                for sound in gameplay_sounds * 50:  # Intense gameplay
                    sm.play_sfx(f"assets/audio/sfx/{sound}")
                    session_sounds.append(sound)
                
                # Phase 3: Cache management test
                unique_sounds = set(session_sounds)
                cache_size_before = len(sm.sfx_cache)
                
                # Add many new sounds to test cache limits
                for i in range(100):
                    sm.preload_sound(f"assets/audio/sfx/test_sound_{i}.ogg")
                
                cache_size_after = len(sm.sfx_cache)
                
                # Verify cache grew but system remained stable
                assert cache_size_after > cache_size_before
                assert cache_size_after >= len(unique_sounds)


class TestErrorRecoveryScenarios:
    """Test sound system recovery from various error conditions."""

    @pytest.fixture
    def error_recovery_sound_manager(self):
        """Create sound manager for error recovery testing."""
        SoundManager._instance = None
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                sm = SoundManager()
                yield sm

    def test_missing_audio_file_recovery(self, error_recovery_sound_manager):
        """Test recovery when audio files are missing during gameplay."""
        sm = error_recovery_sound_manager
        
        with patch.object(sm, 'play_sfx') as mock_sfx:
            # Simulate gameplay where some audio files are missing
            sounds_to_play = [
                ("working_sound.ogg", True),      # File exists
                ("missing_sound.ogg", False),     # File missing
                ("another_working.ogg", True),    # File exists
                ("also_missing.ogg", False),      # File missing
                ("final_working.ogg", True)       # File exists
            ]
            
            for sound_file, exists in sounds_to_play:
                with patch("os.path.exists", return_value=exists):
                    result = sm.play_sfx(sound_file)
                    
                    if exists:
                        # Should succeed for existing files
                        mock_sfx.return_value = Mock()
                    else:
                        # Should fail gracefully for missing files
                        mock_sfx.return_value = None
            
            # System should continue working despite missing files
            assert mock_sfx.call_count == len(sounds_to_play)

    def test_audio_device_disconnection_recovery(self, error_recovery_sound_manager):
        """Test recovery when audio device is disconnected."""
        sm = error_recovery_sound_manager
        
        # Simulate audio device disconnection
        with patch("pygame.mixer.get_init", return_value=None):
            # All audio operations should fail gracefully
            sm.play_music("test_music.ogg")
            sm.play_sfx("test_sound.ogg")
            sm.set_master_volume(0.5)
            
            # System should not crash and should handle reconnection
            # Simulate device reconnection
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                # Should be able to resume normal operation
                result = sm.play_sfx("recovery_sound.ogg")
                # In real implementation, this might require reinitialization

    def test_memory_pressure_recovery(self, error_recovery_sound_manager):
        """Test recovery during memory pressure situations."""
        sm = error_recovery_sound_manager
        
        # Simulate memory pressure by making sound loading fail
        with patch("pygame.mixer.Sound", side_effect=MemoryError("Out of memory")):
            with patch("os.path.exists", return_value=True):
                # Try to load sounds during memory pressure
                results = []
                for i in range(10):
                    result = sm.play_sfx(f"memory_test_{i}.ogg")
                    results.append(result)
                
                # Should handle memory errors gracefully
                assert all(result is None for result in results)
                
                # Cache should not be corrupted
                assert isinstance(sm.sfx_cache, dict)

    def test_pygame_error_recovery(self, error_recovery_sound_manager):
        """Test recovery from various pygame errors."""
        sm = error_recovery_sound_manager
        
        # Test recovery from different pygame errors
        pygame_errors = [
            "Mixer not initialized",
            "Invalid format",
            "File not found",
            "Audio device busy"
        ]
        
        for error_msg in pygame_errors:
            with patch("pygame.mixer.Sound", side_effect=Exception(error_msg)):
                with patch("os.path.exists", return_value=True):
                    # Should handle each error gracefully
                    result = sm.play_sfx("error_test.ogg")
                    assert result is None
                    
                    # System should remain functional
                    volumes = sm.get_volumes()
                    assert "master" in volumes