package com.xiao.medpulse.ui.theme

import android.app.Activity
import android.graphics.Color as AndroidColor
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = LightPrimary,
    primaryContainer = LightSurface,
    onPrimary = LightOnPrimary,
    onPrimaryContainer = LightOnSurface,
    secondary = LightPrimaryVariant,
    background = LightBackground,
    surface = LightSurface,
    surfaceVariant = LightSurface,
    onSurface = LightOnSurface,
    onSurfaceVariant = LightOnSurface.copy(alpha = 0.7f),
    outline = LightOutline
)

private val DarkColorScheme = darkColorScheme(
    primary = DarkPrimary,
    primaryContainer = Color(0xFF2B2930),
    onPrimary = Color(0xFF381E72),
    onPrimaryContainer = DarkOnSurface,
    secondary = DarkPrimaryVariant,
    background = DarkBackground,
    surface = DarkSurface,
    surfaceVariant = Color(0xFF2B2930),
    onSurface = DarkOnSurface,
    onSurfaceVariant = DarkOnSurface.copy(alpha = 0.72f),
    error = DarkError,
    outline = Color(0x66888888)
)

@Composable
fun PocketIrTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val view = LocalView.current

    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = if (darkTheme) AndroidColor.BLACK else AndroidColor.parseColor("#FAFAFA")
            window.navigationBarColor = if (darkTheme) AndroidColor.BLACK else AndroidColor.parseColor("#FAFAFA")
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
            WindowCompat.getInsetsController(window, view).isAppearanceLightNavigationBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}