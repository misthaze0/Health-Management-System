# Health Management System Startup Script
# 健康管理系统启动脚本
# Start all services with background jobs

param(
    [switch]$SkipAI,
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$SkipBrowser,
    [string]$ConfigFile = "startup.config.json"
)

# ========================================
# Configuration Section
# ========================================

# Load external configuration if exists
$script:Config = @{
    Database = @{
        Host = "localhost"
        Port = 3300
        Username = "root"
        Password = "669913"
        Name = "health_management"
    }
    Ports = @{
        Frontend = 19000
        Backend = 19001
        AI = 19002
        MySQL = 3300
    }
    Python = @{
        # Fixed Python path - D:\Anaconda3\python.exe
        PythonPath = "D:\Anaconda3\python.exe"
    }
    Java = @{
        MinVersion = 17
        SearchPaths = @(
            "java"
            "$env:JAVA_HOME\bin\java.exe"
        )
    }
    Maven = @{
        UseWrapper = $true
        SearchPaths = @(
            "mvn"
            "$env:MAVEN_HOME\bin\mvn.cmd"
        )
    }
}

# Load external config if exists
if (Test-Path $ConfigFile) {
    try {
        $externalConfig = Get-Content $ConfigFile | ConvertFrom-Json
        # Merge external config with default
        foreach ($key in $externalConfig.PSObject.Properties.Name) {
            if ($script:Config.ContainsKey($key)) {
                foreach ($subKey in $externalConfig.$key.PSObject.Properties.Name) {
                    $script:Config.$key.$subKey = $externalConfig.$key.$subKey
                }
            }
        }
        Write-Host "[配置] 已加载外部配置文件: $ConfigFile" -ForegroundColor Green
    }
    catch {
        Write-Warning "[警告] 无法加载配置文件 $ConfigFile : $($_.Exception.Message)"
    }
}

# Set encoding for Windows Console
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(936)
$OutputEncoding = [System.Text.Encoding]::GetEncoding(936)
$PSDefaultParameterValues['*:Encoding'] = 'Default'

# Color definitions
$ColorHeader = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "White"

# Project paths
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendPath = Join-Path $ProjectRoot "frontend"
$BackendPath = Join-Path $ProjectRoot "backend"
$AIServicePath = Join-Path $ProjectRoot "ai-service"

# Store background jobs
$global:ServiceJobs = @()

# ========================================
# Utility Functions
# ========================================

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $ColorHeader
    Write-Host "  $Title" -ForegroundColor $ColorHeader
    Write-Host "========================================" -ForegroundColor $ColorHeader
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor $ColorWarning
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERR] $Message" -ForegroundColor $ColorError
}

function Write-Info {
    param([string]$Message)
    Write-Host "[->] $Message" -ForegroundColor $ColorInfo
}

# Check if command exists
function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Find executable in search paths
function Find-Executable {
    param(
        [string]$Name,
        [string[]]$SearchPaths
    )
    foreach ($path in $SearchPaths) {
        if (Test-Path $path) {
            return $path
        }
        if (Test-Command $path) {
            return $path
        }
    }
    return $null
}

# Check Java version
function Test-JavaVersion {
    param([int]$MinVersion = 17)
    try {
        $javaPath = Find-Executable -Name "java" -SearchPaths $script:Config.Java.SearchPaths
        if (-not $javaPath) {
            return @{ Success = $false; Message = "未找到Java" }
        }
        
        $versionOutput = & $javaPath -version 2>&1
        $versionString = $versionOutput | Select-String -Pattern '"(\d+)' | ForEach-Object { $_.Matches.Groups[1].Value }
        
        if ($versionString -and [int]$versionString -ge $MinVersion) {
            return @{ 
                Success = $true; 
                Version = $versionString; 
                Path = $javaPath 
            }
        }
        else {
            return @{ 
                Success = $false; 
                Message = "Java版本过低: $versionString, 需要 $MinVersion+" 
            }
        }
    }
    catch {
        return @{ Success = $false; Message = "检查Java版本失败: $($_.Exception.Message)" }
    }
}

# Check MySQL connection
function Test-MySQLConnection {
    param(
        [string]$DbHost = $script:Config.Database.Host,
        [int]$DbPort = $script:Config.Database.Port,
        [string]$DbUsername = $script:Config.Database.Username,
        [string]$DbPassword = $script:Config.Database.Password
    )
    
    try {
        # First check if port is open
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connection = $tcpClient.BeginConnect($DbHost, $DbPort, $null, $null)
        $success = $connection.AsyncWaitHandle.WaitOne(2000, $false)
        if (-not $success) {
            return $false
        }
        $tcpClient.EndConnect($connection)
        $tcpClient.Close()
        
        # Try to execute mysql command to verify connection
        $mysqlCmd = "mysql -h $DbHost -P $DbPort -u $DbUsername -p$DbPassword -e 'SELECT 1' 2>`$null"
        $result = Invoke-Expression $mysqlCmd
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Start MySQL service with retry
function Start-MySQLService {
    param([int]$MaxRetries = 3)
    
    Write-Header "Starting MySQL Service"
    
    for ($retry = 1; $retry -le $MaxRetries; $retry++) {
        Write-Info "尝试启动MySQL (第 $retry/$MaxRetries 次)..."
        
        # Check if MySQL service exists and start it
        $mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue | Select-Object -First 1
        
        if ($mysqlService) {
            Write-Info "找到MySQL服务: $($mysqlService.Name)"
            if ($mysqlService.Status -ne "Running") {
                try {
                    Start-Service -Name $mysqlService.Name -ErrorAction Stop
                    Write-Success "MySQL服务已启动"
                }
                catch {
                    Write-ErrorMsg "启动MySQL服务失败: $($_.Exception.Message)"
                    if ($retry -lt $MaxRetries) {
                        Start-Sleep -Seconds 2
                        continue
                    }
                    return $false
                }
            }
            else {
                Write-Success "MySQL服务已在运行"
            }
        }
        else {
            # Try to start mysqld directly
            $mysqldPaths = @(
                "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
                "C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqld.exe"
                "C:\mysql\bin\mysqld.exe"
                "D:\mysql\bin\mysqld.exe"
                "$env:USERPROFILE\mysql\bin\mysqld.exe"
            )
            
            $mysqldFound = $false
            foreach ($path in $mysqldPaths) {
                if (Test-Path $path) {
                    Write-Info "从以下路径启动MySQL: $path"
                    try {
                        Start-Process -FilePath $path -ArgumentList "--console" -WindowStyle Hidden
                        $mysqldFound = $true
                        break
                    }
                    catch {
                        Write-Warning "无法从 $path 启动MySQL"
                    }
                }
            }
            
            if (-not $mysqldFound) {
                Write-ErrorMsg "未找到MySQL服务或mysqld.exe"
                if ($retry -lt $MaxRetries) {
                    Start-Sleep -Seconds 2
                    continue
                }
                return $false
            }
        }
        
        # Wait for MySQL to be ready
        Write-Info "等待MySQL就绪..."
        $maxAttempts = 30
        $attempt = 0
        
        while ($attempt -lt $maxAttempts) {
            if (Test-MySQLConnection) {
                Write-Success "MySQL已就绪"
                return $true
            }
            Start-Sleep -Seconds 2
            $attempt++
            Write-Info "等待MySQL... ($attempt/$maxAttempts)"
        }
        
        if ($retry -lt $MaxRetries) {
            Write-Warning "MySQL启动超时，正在重试..."
            Start-Sleep -Seconds 3
        }
    }
    
    Write-ErrorMsg "MySQL在 $MaxRetries 次尝试后仍无法启动"
    return $false
}

# Initialize database with better error handling
function Initialize-Database {
    param([string]$InitScriptPath)
    
    Write-Header "Initializing Database"
    
    # Check if database exists
    $checkDbCmd = "mysql -h $($script:Config.Database.Host) -P $($script:Config.Database.Port) -u $($script:Config.Database.Username) -p$($script:Config.Database.Password) -e `"SHOW DATABASES LIKE '$($script:Config.Database.Name)'`" 2>`$null"
    $dbExists = Invoke-Expression $checkDbCmd
    
    if ($dbExists -and $dbExists -like "*$($script:Config.Database.Name)*") {
        Write-Success "数据库 '$($script:Config.Database.Name)' 已存在"
        return $true
    }
    
    # Check if init script exists
    if (-not (Test-Path $InitScriptPath)) {
        Write-Warning "数据库初始化脚本未找到: $InitScriptPath"
        return $false
    }
    
    Write-Info "从初始化脚本创建数据库..."
    try {
        $initCmd = "mysql -h $($script:Config.Database.Host) -P $($script:Config.Database.Port) -u $($script:Config.Database.Username) -p$($script:Config.Database.Password) < `"$InitScriptPath`" 2>`$null"
        Invoke-Expression $initCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "数据库初始化成功"
            return $true
        }
        else {
            Write-ErrorMsg "数据库初始化失败"
            return $false
        }
    }
    catch {
        Write-ErrorMsg "初始化数据库时出错: $($_.Exception.Message)"
        return $false
    }
}

# Check if port is in use
function Test-PortInUse {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                      Where-Object { $_.State -eq "Listen" }
        return $null -ne $connection
    }
    catch {
        return $false
    }
}

# Stop process using port with better error handling
function Stop-ProcessByPort {
    param([int]$Port)
    
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                       Where-Object { $_.State -eq "Listen" -and $_.OwningProcess -gt 4 }
        
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Warning "停止端口 $Port 上的进程: $($process.ProcessName) (PID: $($process.Id))"
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Seconds 2
    }
    catch {
        Write-Warning "停止端口 $Port 的进程时出错: $($_.Exception.Message)"
    }
}

# Wait for service to be ready with health check
function Wait-ForService {
    param(
        [string]$Name,
        [int]$Port,
        [string]$HealthUrl = $null,
        [int]$TimeoutSeconds = 60
    )
    
    Write-Info "等待 $Name 就绪 (端口: $Port)..."
    $elapsed = 0
    
    while ($elapsed -lt $TimeoutSeconds) {
        # Check port
        if (Test-PortInUse -Port $Port) {
            # If health URL provided, check it
            if ($HealthUrl) {
                try {
                    $response = Invoke-WebRequest -Uri $HealthUrl -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
                    if ($response.StatusCode -eq 200) {
                        Write-Success "$Name 已就绪并通过健康检查"
                        return $true
                    }
                }
                catch {
                    # Health check failed, continue waiting
                }
            }
            else {
                Write-Success "$Name 已就绪"
                return $true
            }
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }
    
    Write-Warning "$Name 启动超时"
    return $false
}

# Stop all services gracefully
function Stop-AllServices {
    Write-Host ""
    Write-Header "Stopping all services..."
    
    # Stop all background jobs
    foreach ($job in $global:ServiceJobs) {
        if ($job -and $job.State -ne "Completed") {
            Write-Info "停止任务: $($job.Name)"
            Stop-Job -Job $job -ErrorAction SilentlyContinue
            Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Close processes using ports
    foreach ($port in $script:Config.Ports.Values) {
        if ($port -ne $script:Config.Ports.MySQL) {
            Stop-ProcessByPort -Port $port
        }
    }
    
    Write-Success "所有服务已停止"
}

# Register exit event
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Stop-AllServices
}

# ========================================
# Main Program
# ========================================

Write-Header "Health Management System Launcher"
Write-Info "项目路径: $ProjectRoot"
Write-Host ""

# Check and start MySQL first
Write-Header "Checking Database Connection"
Write-Info "检查MySQL连接 (端口 $($script:Config.Database.Port))..."

$mysqlReady = Test-MySQLConnection
if (-not $mysqlReady) {
    Write-Warning "MySQL未运行或无法访问"
    Write-Info "尝试启动MySQL服务..."
    
    $mysqlStarted = Start-MySQLService -MaxRetries 3
    if (-not $mysqlStarted) {
        Write-ErrorMsg "自动启动MySQL失败"
        Write-Host ""
        Write-Host "请手动启动MySQL:" -ForegroundColor $ColorWarning
        Write-Host "  1. 打开服务 (services.msc)" -ForegroundColor $ColorInfo
        Write-Host "  2. 找到MySQL服务并启动" -ForegroundColor $ColorInfo
        Write-Host "  3. 或运行: net start MySQL80" -ForegroundColor $ColorInfo
        Write-Host ""
        $continue = Read-Host "是否继续（无数据库）? (Y/N)"
        if ($continue.ToUpper() -ne "Y") {
            exit 1
        }
    }
    else {
        # Initialize database if needed
        $initScript = Join-Path $ProjectRoot "database\init.sql"
        Initialize-Database -InitScriptPath $initScript
    }
}
else {
    Write-Success "MySQL已在运行"
    # Check and initialize database
    $initScript = Join-Path $ProjectRoot "database\init.sql"
    Initialize-Database -InitScriptPath $initScript
}

Write-Host ""

# Clean ports
Write-Header "Cleaning port usage"
foreach ($service in $script:Config.Ports.GetEnumerator()) {
    if ($service.Key -eq "MySQL") { continue }
    if (-not (Get-Variable -Name "Skip$($service.Key)" -ValueOnly -ErrorAction SilentlyContinue)) {
        Write-Info "检查端口 $($service.Value) ($($service.Key))..."
        Stop-ProcessByPort -Port $service.Value
    }
}
Write-Host ""

# Environment check
Write-Header "Environment Check"

# Check Java
if (-not $SkipBackend) {
    $javaCheck = Test-JavaVersion -MinVersion $script:Config.Java.MinVersion
    if ($javaCheck.Success) {
        Write-Success "Java: 版本 $($javaCheck.Version)"
        $script:JavaPath = $javaCheck.Path
    }
    else {
        Write-ErrorMsg $javaCheck.Message
        exit 1
    }
}

# Check Maven or Maven Wrapper
if (-not $SkipBackend) {
    $mvnWrapperPath = Join-Path $BackendPath "mvnw.cmd"
    if ($script:Config.Maven.UseWrapper -and (Test-Path $mvnWrapperPath)) {
        Write-Success "Maven: 使用Wrapper ($mvnWrapperPath)"
        $script:MavenCmd = $mvnWrapperPath
    }
    else {
        $mavenPath = Find-Executable -Name "mvn" -SearchPaths $script:Config.Maven.SearchPaths
        if ($mavenPath) {
            Write-Success "Maven: 已安装 ($mavenPath)"
            $script:MavenCmd = $mavenPath
        }
        else {
            Write-Warning "Maven未安装，尝试使用Maven Wrapper..."
            if (Test-Path $mvnWrapperPath) {
                $script:MavenCmd = $mvnWrapperPath
                Write-Success "Maven: 使用Wrapper"
            }
            else {
                Write-ErrorMsg "未找到Maven或Maven Wrapper"
                exit 1
            }
        }
    }
}

# Check Node.js
if (-not $SkipFrontend) {
    if (Test-Command "node") {
        $nodeVersion = node --version
        Write-Success "Node.js: $nodeVersion"
    }
    else {
        Write-ErrorMsg "Node.js未安装"
        exit 1
    }
}

# Check Python - Use fixed path
if (-not $SkipAI) {
    $pythonPath = $script:Config.Python.PythonPath
    
    if (Test-Path $pythonPath) {
        $pyVersion = & $pythonPath --version 2>&1
        Write-Success "Python: $pyVersion ($pythonPath)"
        $script:PythonPath = $pythonPath
    }
    else {
        Write-ErrorMsg "Python not found at: $pythonPath"
        Write-Host "Please check the Python path configuration" -ForegroundColor $ColorWarning
        exit 1
    }
}

Write-Host ""

# Start AI Service
if (-not $SkipAI) {
    Write-Header "Starting AI Service"
    
    Write-Info "使用Python: $($script:PythonPath)"
    
    $aiJob = Start-Job -Name "AI-Service" -ScriptBlock {
        param($Path, $Python)
        Set-Location $Path
        & $Python main.py
    } -ArgumentList $AIServicePath, $script:PythonPath
    
    $global:ServiceJobs += $aiJob
    Write-Info "AI服务任务已启动 (ID: $($aiJob.Id))"
    
    # Wait for service ready
    Wait-ForService -Name "AI Service" -Port $script:Config.Ports.AI -TimeoutSeconds 60
}

# Start Backend Service
if (-not $SkipBackend) {
    Write-Header "Starting Backend Service"
    
    $backendJob = Start-Job -Name "Backend-Service" -ScriptBlock {
        param($Path, $Maven)
        Set-Location $Path
        $env:JAVA_TOOL_OPTIONS = "-Dfile.encoding=GBK -Dsun.stdout.encoding=GBK -Dsun.stderr.encoding=GBK"
        & $Maven spring-boot:run
    } -ArgumentList $BackendPath, $script:MavenCmd
    
    $global:ServiceJobs += $backendJob
    Write-Info "后端服务任务已启动 (ID: $($backendJob.Id))"
    
    # Wait for service ready with health check
    $healthUrl = "http://localhost:$($script:Config.Ports.Backend)/api/actuator/health"
    Wait-ForService -Name "Backend Service" -Port $script:Config.Ports.Backend -HealthUrl $healthUrl -TimeoutSeconds 90
}

# Start Frontend Service
if (-not $SkipFrontend) {
    Write-Header "Starting Frontend Service"
    
    # Check node_modules
    if (-not (Test-Path "$FrontendPath\node_modules")) {
        Write-Warning "未找到node_modules，正在安装依赖..."
        Set-Location $FrontendPath
        npm install
        Set-Location $ProjectRoot
    }
    
    $frontendJob = Start-Job -Name "Frontend-Service" -ScriptBlock {
        param($Path)
        Set-Location $Path
        npm run dev
    } -ArgumentList $FrontendPath
    
    $global:ServiceJobs += $frontendJob
    Write-Info "前端服务任务已启动 (ID: $($frontendJob.Id))"
    
    # Wait for service ready
    Wait-ForService -Name "Frontend Service" -Port $script:Config.Ports.Frontend -TimeoutSeconds 30
}

# Show service status
Write-Host ""
Write-Header "Service Status"

$allReady = $true

if (-not $SkipAI) {
    $aiReady = Test-PortInUse -Port $script:Config.Ports.AI
    if ($aiReady) {
        Write-Success "AI服务: http://localhost:$($script:Config.Ports.AI)"
    }
    else {
        Write-Warning "AI服务: 可能仍在启动中"
        $allReady = $false
    }
}

if (-not $SkipBackend) {
    $backendReady = Test-PortInUse -Port $script:Config.Ports.Backend
    if ($backendReady) {
        Write-Success "后端服务: http://localhost:$($script:Config.Ports.Backend)/api"
    }
    else {
        Write-Warning "后端服务: 可能仍在启动中"
        $allReady = $false
    }
}

if (-not $SkipFrontend) {
    $frontendReady = Test-PortInUse -Port $script:Config.Ports.Frontend
    if ($frontendReady) {
        Write-Success "前端服务: http://localhost:$($script:Config.Ports.Frontend)"
    }
    else {
        Write-Warning "前端服务: 可能仍在启动中"
        $allReady = $false
    }
}

Write-Host ""
Write-Host "API文档: http://localhost:$($script:Config.Ports.Backend)/api/swagger-ui.html" -ForegroundColor $ColorInfo
Write-Host ""

if ($allReady) {
    Write-Header "所有服务启动成功"
}
else {
    Write-Header "服务已启动（部分可能需要更多时间）"
}

# Auto open browser
if (-not $SkipFrontend -and -not $SkipBrowser) {
    $frontendReady = Test-PortInUse -Port $script:Config.Ports.Frontend
    if ($frontendReady) {
        $clearAuthUrl = "http://localhost:$($script:Config.Ports.Frontend)/clear-auth.html"
        Write-Info "打开浏览器清除认证状态: $clearAuthUrl"
        try {
            Start-Process $clearAuthUrl
            Write-Success "浏览器已打开（清除认证状态）"
        }
        catch {
            Write-Warning "无法自动打开浏览器"
        }
    }
    else {
        Write-Warning "前端未就绪，跳过自动打开浏览器"
    }
}

Write-Host ""
Write-Host "选项:" -ForegroundColor $ColorHeader
Write-Host "  [L] 查看服务日志 / View service logs" -ForegroundColor $ColorInfo
Write-Host "  [S] 查看服务状态 / View service status" -ForegroundColor $ColorInfo
Write-Host "  [Q] 停止所有服务并退出 / Stop all services and quit" -ForegroundColor $ColorInfo
Write-Host ""

# Interactive loop
while ($true) {
    $key = Read-Host "选择选项 (L/S/Q)"
    
    switch ($key.ToUpper()) {
        "L" {
            Write-Host ""
            Write-Header "Service Logs"
            foreach ($job in $global:ServiceJobs) {
                Write-Host "--- $($job.Name) ---" -ForegroundColor $ColorHeader
                Receive-Job -Job $job -Keep | Select-Object -Last 20
                Write-Host ""
            }
        }
        "S" {
            Write-Host ""
            Write-Header "Service Status"
            Get-Job | Select-Object Name, State, Command | Format-Table -AutoSize
            
            Write-Host "端口状态:" -ForegroundColor $ColorHeader
            foreach ($service in $script:Config.Ports.GetEnumerator()) {
                $inUse = Test-PortInUse -Port $service.Value
                $status = if ($inUse) { "使用中" } else { "空闲" }
                $color = if ($inUse) { $ColorSuccess } else { $ColorWarning }
                Write-Host "  $($service.Key) (端口 $($service.Value)): $status" -ForegroundColor $color
            }
        }
        "Q" {
            Stop-AllServices
            exit 0
        }
        default {
            Write-Warning "无效选择，请按 L, S 或 Q"
        }
    }
}
